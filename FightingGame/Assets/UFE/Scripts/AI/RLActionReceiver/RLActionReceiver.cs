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

    private bool isMatchActive = false;

    private bool cooldownLogged = false;
    private bool boostLogged = false;

    void Start()
    {
        actionPath = Application.persistentDataPath + "/rl_action.json";
        Debug.Log("🤖 RLActionReceiver path: " + actionPath);

    }

    void OnEnable()
    {
        UFE.OnGameBegin += OnGameBegin;
        UFE.OnRoundBegins += OnRoundBegin;
        UFE.OnRoundEnds += OnRoundEnd;
        UFE.OnGameEnds += OnGameEnds;
    }

    void OnDisable()
    {
        UFE.OnGameBegin -= OnGameBegin;
        UFE.OnRoundBegins -= OnRoundBegin;
        UFE.OnRoundEnds -= OnRoundEnd;
        UFE.OnGameEnds -= OnGameEnds;
    }

    void OnGameBegin(
        CharacterInfo p1Info,
        CharacterInfo p2Info,
        StageOptions stage
    )
    {
        p1 = UFE.GetControlsScript(1);
        p2 = UFE.GetControlsScript(2);

        Debug.Log("✅ RLActionReceiver: Match Started");

        if (p1 != null && p2 != null)
        {
            Debug.Log(
                "P1 = " + p1.myInfo.characterName +
                " | P2 = " + p2.myInfo.characterName
            );
        }
    }

    void OnRoundBegin(int round)
    {
        isMatchActive = true;

        currentAction = "NONE";

        boostTimer = 0f;
        cooldownTimer = 0f;

        ResetAll();

        Debug.Log("🔥 ROUND START");
    }

    void OnRoundEnd(
        CharacterInfo winner,
        CharacterInfo loser
    )
    {
        isMatchActive = false;

        currentAction = "NONE";

        boostTimer = 0f;
        cooldownTimer = 0f;

        ResetAll();

        Debug.Log("🛑 ROUND END → RL disabled");
    }

    void OnGameEnds(
        CharacterInfo winner,
        CharacterInfo loser
    )
    {
        Debug.Log("🛑 Match End");

        p1 = null;
        p2 = null;

        ResetAll();
    }

    void Update()
    {
        if (p1 == null || p2 == null) return;
        
        if (!isMatchActive) return;

        // =====================================================
        // BOOST ACTIVE
        // =====================================================

        if (boostTimer > 0)
        {
            boostTimer -= Time.deltaTime;

            if (!boostLogged)
            {
                Debug.Log(
                    "🔥 BOOST ACTIVE → " +
                    currentAction +
                    " | Duration: " +
                    boostDuration
                );

                boostLogged = true;
            }

            if (boostTimer <= 0)
            {
                ResetAll();

                cooldownTimer = cooldownDuration;

                Debug.Log("⏳ BOOST ENDED");

                boostLogged = false;
                cooldownLogged = false;

                currentAction = "NONE";
            }

            return;
        }

        // =====================================================
        // COOLDOWN
        // =====================================================

        if (cooldownTimer > 0)
        {
            cooldownTimer -= Time.deltaTime;

            if (!cooldownLogged)
            {
                Debug.Log(
                    "🧊 COOLDOWN START → " +
                    cooldownDuration +
                    "s"
                );

                cooldownLogged = true;
            }

            if (cooldownTimer <= 0)
            {
                Debug.Log("✅ COOLDOWN FINISHED");

                cooldownLogged = false;
            }

            return;
        }

        // =====================================================
        // CHECK INTERVAL
        // =====================================================

        if (Time.time - lastCheckTime < checkInterval)
        {
            return;
        }

        lastCheckTime = Time.time;

        Debug.Log("🔍 Checking action file...");

        // =====================================================
        // FILE EXISTS
        // =====================================================

        if (!File.Exists(actionPath))
        {
            Debug.LogWarning("❌ Action file not found");
            return;
        }

        // =====================================================
        // READ JSON
        // =====================================================

        string json = "";

        try
        {
            json = File.ReadAllText(actionPath);

            Debug.Log("📄 JSON: " + json);
        }
        catch
        {
            Debug.LogWarning("⚠️ Cannot read action file");
            return;
        }

        if (string.IsNullOrEmpty(json))
        {
            Debug.LogWarning("⚠️ Empty JSON");
            return;
        }

        // =====================================================
        // PARSE JSON
        // =====================================================

        RLAction action = null;

        try
        {
            action = JsonUtility.FromJson<RLAction>(json);

            Debug.Log(
                "🧠 Parsed Action: " +
                action.action +
                " | value=" +
                action.value
            );
        }
        catch
        {
            Debug.LogWarning("⚠️ JSON parse failed");
            return;
        }

        if (action == null)
        {
            Debug.LogWarning("⚠️ Action null");
            return;
        }

        // =====================================================
        // SAME ACTION FILTER
        // =====================================================

        // if (action.action == currentAction)
        // {
        //     Debug.Log(
        //         "⏭ SAME ACTION SKIPPED: " +
        //         action.action
        //     );

        //     return;
        // }

        // =====================================================
        // APPLY
        // =====================================================

        Debug.Log(
            "🚀 APPLY ACTION: " +
            action.action
        );

        ApplyAction(action);

        currentAction = action.action;

        boostTimer = boostDuration;

        Debug.Log(
            "✅ BOOST STARTED | Duration: " +
            boostDuration
        );
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