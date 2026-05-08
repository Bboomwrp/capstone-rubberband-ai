using UnityEngine;
using System.Collections;
using System.IO;

public class RLActionReceiver : MonoBehaviour
{
    private ControlsScript p1;
    private ControlsScript p2;

    private string actionPath;

    private float checkInterval = 1f;
    private float lastCheckTime = 0f;

    private float boostDuration = 2f;
    private float cooldownDuration = 1f;

    private float boostTimer = 0f;
    private float cooldownTimer = 0f;

    private string currentAction = "NONE";

    void Start()
    {
        actionPath = Application.persistentDataPath + "/rl_action.json";
        Debug.Log("🤖 RLActionReceiver path: " + actionPath);

        StartCoroutine(FindPlayers());
    }

    IEnumerator FindPlayers()
    {
        yield return new WaitForSeconds(1f);

        p1 = UFE.GetControlsScript(1);
        p2 = UFE.GetControlsScript(2);

        if (p1 == null || p2 == null)
        {
            Debug.LogError("❌ RLActionReceiver: Players not found!");
        }
        else
        {
            Debug.Log("✅ RLActionReceiver: Players Ready");
        }
    }

    void Update()
    {
        if (p1 == null || p2 == null) return;

        if (boostTimer > 0)
        {
            boostTimer -= Time.deltaTime;

            if (boostTimer <= 0)
            {
                ResetAll();
                cooldownTimer = cooldownDuration;
                currentAction = "NONE";
                Debug.Log("⏳ Boost ended → cooldown");
            }

            return; // lock ระหว่าง boost
        }

        if (cooldownTimer > 0)
        {
            cooldownTimer -= Time.deltaTime;
            return;
        }

        if (Time.time - lastCheckTime < checkInterval) return;
        lastCheckTime = Time.time;

        if (!File.Exists(actionPath)) return;

        string json = "";

        try
        {
            json = File.ReadAllText(actionPath);
        }
        catch
        {
            Debug.LogWarning("⚠️ Cannot read action file");
            return;
        }

        if (string.IsNullOrEmpty(json)) return;

        RLAction action = null;

        try
        {
            action = JsonUtility.FromJson<RLAction>(json);
        }
        catch
        {
            Debug.LogWarning("⚠️ JSON parse failed");
            return;
        }

        if (action == null) return;

        if (action.action == currentAction) return;

        ApplyAction(action);

        currentAction = action.action;
        boostTimer = boostDuration;
    }

    void ApplyAction(RLAction action)
    {
        float p1HP = p1.myInfo.currentLifePoints;
        float p2HP = p2.myInfo.currentLifePoints;

        // เลือกฝั่งที่เสียเปรียบ
        ControlsScript target = (p1HP < p2HP) ? p1 : p2;

        float value = Mathf.Clamp(action.value, 0.8f, 1.3f);

        if (action.action == "BOOST_ATTACK")
        {
            target.attackMultiplier = value;
            Debug.Log("🔥 BOOST_ATTACK → P" + target.playerNum + " x" + value);
        }
        else if (action.action == "BOOST_DEFENSE")
        {
            target.defenseMultiplier = value;
            Debug.Log("🛡 BOOST_DEFENSE → P" + target.playerNum + " x" + value);
        }
        else if (action.action == "BOOST_GAUGE")
        {
            target.gaugeGainMultiplier = value;
            Debug.Log("⚡ BOOST_GAUGE → P" + target.playerNum + " x" + value);
        }
        else if (action.action == "NONE")
        {
            ResetAll();
        }
    }

    void ResetAll()
    {
        if (p1 != null)
        {
            p1.attackMultiplier = 1f;
            p1.defenseMultiplier = 1f;
            p1.gaugeGainMultiplier = 1f;
        }

        if (p2 != null)
        {
            p2.attackMultiplier = 1f;
            p2.defenseMultiplier = 1f;
            p2.gaugeGainMultiplier = 1f;
        }

        Debug.Log("🔄 Reset multipliers");
    }

    [System.Serializable]
    public class RLAction
    {
        public string action;
        public float value;
    }
}