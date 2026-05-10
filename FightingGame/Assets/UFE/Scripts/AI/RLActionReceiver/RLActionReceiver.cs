using UnityEngine;
using System.Collections;
using System.IO;
using UnityEngine.UI;

public class RLActionReceiver : MonoBehaviour
{
    private ControlsScript p1;
    private ControlsScript p2;

    private string actionPath;

    private float checkInterval = 0.2f;
    private float lastCheckTime = 0f;

    private float boostDuration = 5f;
    private float cooldownDuration = 3f;

    private float boostTimer = 0f;
    private float cooldownTimer = 0f;

    private string currentAction = "NONE";

    private bool isMatchActive = false;

    private bool cooldownLogged = false;
    private bool boostLogged = false;

    private ControlsScript boostedTarget;

    public Text p1BoostText;
    public Text p2BoostText;

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
        ResetActionFile();

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
        ResetActionFile();

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
        ResetActionFile();
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

            if (ShouldCancelBoost())
            {
                Debug.Log("🛑 BOOST CANCELLED");

                ResetAll();

                boostTimer = 0f;

                cooldownTimer = cooldownDuration;

                currentAction = "NONE";

                return;
            }

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

        if (action.action != "NONE")
        {
            boostTimer = boostDuration;
        }

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
        boostedTarget = target;
        float value = Mathf.Clamp(action.value, 0.8f, 1.4f);

        if (action.action == "BOOST_ATTACK")
        {
            target.attackMultiplier = value;
            ShowBoostUI(
                target,
                "BOOST ATK",
                Color.red
            );
            Debug.Log(
                "🔥 BOOST_ATTACK → P" +
                target.playerNum +
                " | value=" + value +
                " | actual=" + target.attackMultiplier
            );
        }
        else if (action.action == "BOOST_DEFENSE")
        {
            target.defenseMultiplier = value;
            ShowBoostUI(
                target,
                "BOOST DEF",
                Color.green
            );
            Debug.Log(
                "🛡 BOOST_DEFENSE → P" +
                target.playerNum +
                " | value=" + value +
                " | actual=" + target.defenseMultiplier
            );
        }
        else if (action.action == "BOOST_GAUGE")
        {
            target.gaugeGainMultiplier = value;
            ShowBoostUI(
                target,
                "BOOST GAUGE",
                Color.cyan
            );
            Debug.Log(
                "⚡ BOOST_GAUGE → P" +
                target.playerNum +
                " | value=" + value +
                " | actual=" + target.gaugeGainMultiplier
            );
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

        if (p1BoostText != null)
            p1BoostText.gameObject.SetActive(false);

        if (p2BoostText != null)
            p2BoostText.gameObject.SetActive(false);

        boostedTarget = null;

        Debug.Log("🔄 Reset multipliers");
    }

    void ResetActionFile()
    {
        RLAction resetAction = new RLAction();

        resetAction.action = "NONE";
        resetAction.value = 1.0f;

        string json = JsonUtility.ToJson(resetAction);

        try
        {
            File.WriteAllText(actionPath, json);

            Debug.Log("🧹 Reset rl_action.json");
        }
        catch
        {
            Debug.LogWarning("⚠ Cannot reset action file");
        }
    }

    bool ShouldCancelBoost()
    {
        if (p1 == null || p2 == null)
            return false;

        float p1HP =
            p1.myInfo.currentLifePoints /
            p1.myInfo.lifePoints;

        float p2HP =
            p2.myInfo.currentLifePoints /
            p2.myInfo.lifePoints;

        float hpDiff = Mathf.Abs(p1HP - p2HP);

        // CLOSE MATCH

        if (hpDiff < 0.075f)
        {
            Debug.Log("⚖ CLOSE MATCH → CANCEL BOOST");
            return true;
        }

        // LOW HP FINISH

        if (p1HP < 0.10f && p2HP < 0.10f)
        {
            Debug.Log("🏁 LOW HP FINISH → CANCEL BOOST");
            return true;
        }

        // EARLY GAME

        if (p1HP > 0.90f && p2HP > 0.90f)
        {
            Debug.Log("🚫 EARLY GAME → CANCEL BOOST");
            return true;
        }

        // TARGET NOW WINNING

        ControlsScript boosted =
            GetCurrentlyBoostedPlayer();

        if (boosted != null)
        {
            bool p1Boosted =
                boosted.playerNum == 1;

            // boosted player now leading
            if (p1Boosted && p1HP > p2HP)
            {
                Debug.Log("🔄 P1 RECOVERED → CANCEL BOOST");
                return true;
            }

            if (!p1Boosted && p2HP > p1HP)
            {
                Debug.Log("🔄 P2 RECOVERED → CANCEL BOOST");
                return true;
            }
        }

        return false;
    }

    void ShowBoostUI(
        ControlsScript target,
        string text,
        Color color
    )
    {
        Text ui =
            (target.playerNum == 1)
            ? p1BoostText
            : p2BoostText;

        ui.text = text;
        ui.color = color;

        ui.gameObject.SetActive(true);

    }

    ControlsScript GetCurrentlyBoostedPlayer()
    {
        if (boostedTarget == null)
            return null;

        return boostedTarget;
    }

    public string GetCurrentAction()
    {
        return currentAction;
    }

    public bool IsBoostActive()
    {
        return boostTimer > 0f;
    }

    [System.Serializable]
    public class RLAction
    {
        public string action;
        public float value;
    }
}