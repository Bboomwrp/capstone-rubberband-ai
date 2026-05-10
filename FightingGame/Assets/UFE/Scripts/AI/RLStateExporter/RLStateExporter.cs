using UnityEngine;
using System.Collections;
using System.IO;

public class RLStateExporter : MonoBehaviour
{
    private ControlsScript p1;
    private ControlsScript p2;

    private RLActionReceiver actionReceiver;

    private string filePath;

    private bool matchStarted = false;

    private float interval = 1f;
    private float lastTime = 0f;

    private bool isFighting = false;
    private bool doneSent = false;

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

    void OnGameBegin(CharacterInfo p1Info, CharacterInfo p2Info, StageOptions stage)
    {
        p1 = UFE.GetControlsScript(1);
        p2 = UFE.GetControlsScript(2);

        filePath = Application.persistentDataPath + "/rl_state.json";

        Debug.Log("🧠 RLStateExporter Started: " + filePath);

        matchStarted = true;
        lastTime = Time.time;
    }

    void OnRoundBegin(int round)
    {
        isFighting = true;
        doneSent = false;

        Debug.Log("🔥 Round Started: " + round);
    }

    void OnRoundEnd(CharacterInfo winner, CharacterInfo loser)
    {
        isFighting = false;

        if (!doneSent)
        {
            ExportState(true);

            doneSent = true;
        }

        string winName = (winner != null) ? winner.characterName : "Unknown";
        Debug.Log("🟦 Round End: " + winName);
    }

    void Update()
    {
        if (!matchStarted) return;
        if (p1 == null || p2 == null) return;

        if (!doneSent && (p1.myInfo.currentLifePoints <= 0 || p2.myInfo.currentLifePoints <= 0))
        {
            ExportState(true);
            doneSent = true;

            // Debug.Log("✅ DONE (HP KO DETECT)");
            return;
        }

        if (!isFighting) return;

        if (Time.time - lastTime >= interval)
        {
            lastTime = Time.time;
            if (!isFighting)
                return;
            ExportState(false);
        }

        if (UFE.GetTimer() >= UFE.config.roundOptions.timer) return;
    }

    void ExportState(bool doneFlag)
    {
        actionReceiver = FindObjectOfType<RLActionReceiver>();

        string current_action;
        bool is_boost_active;
        if (actionReceiver != null)
        {
            current_action = actionReceiver.GetCurrentAction();

            is_boost_active = actionReceiver.IsBoostActive();
        }
        else
        {
            current_action = "NONE";
            is_boost_active = false;
        }

        float p1MaxHP = p1.myInfo.lifePoints;
        float p2MaxHP = p2.myInfo.lifePoints;
        
        float p1HP = p1.myInfo.currentLifePoints;
        float p2HP = p2.myInfo.currentLifePoints;
        
        float p1HPRatio = p1HP / p1MaxHP;
        float p2HPRatio = p2HP / p2MaxHP;

        // if (p1HP <= 0 || p2HP <= 0)
        // {
        //     Debug.Log("⚠️ KO DETECTED | doneSent=" + doneSent + " | isFighting=" + isFighting);
        // }

        float hpRatioDiff = p1HPRatio - p2HPRatio;

        float p1Gauge = p1.myInfo.currentGaugePoints;
        float p2Gauge = p2.myInfo.currentGaugePoints;

        float p1GaugeRatio = p1.myInfo.maxGaugePoints > 0 ? p1Gauge / p1.myInfo.maxGaugePoints : 0;
        float p2GaugeRatio = p2.myInfo.maxGaugePoints > 0 ? p2Gauge / p2.myInfo.maxGaugePoints : 0;

        float p1UltraGauge = p1.myInfo.currentUltraGaugePoints;
        float p2UltraGauge = p2.myInfo.currentUltraGaugePoints;

        float p1UltraGaugeRatio = p1.myInfo.maxUltraGauge > 0 ? p1UltraGauge / p1.myInfo.maxUltraGauge : 0;
        float p2UltraGaugeRatio = p2.myInfo.maxUltraGauge > 0 ? p2UltraGauge / p2.myInfo.maxUltraGauge : 0;

        float distance = Mathf.Abs(
            p1.transform.position.x - p2.transform.position.x
        );

        float timer = UFE.GetTimer();
        float maxTime = UFE.config.roundOptions.timer;

        float timeRemaining = timer / maxTime;
        timeRemaining = Mathf.Clamp01(timeRemaining);

        bool isKO = p1HP <= 0 || p2HP <= 0;

        RLState state = new RLState();
        state.hp_ratio_diff = hpRatioDiff;
        state.p1_hp_ratio = p1HPRatio;
        state.p2_hp_ratio = p2HPRatio;
        state.p1_gauge_ratio = p1GaugeRatio;
        state.p2_gauge_ratio = p2GaugeRatio;
        state.p1_ultra_gauge_ratio = p1UltraGaugeRatio;
        state.p2_ultra_gauge_ratio = p2UltraGaugeRatio;
        state.p1_character = p1.myInfo.characterName;
        state.p2_character = p2.myInfo.characterName;
        state.current_action = current_action;
        state.is_boost_active = is_boost_active;
        state.distance = distance;
        state.time = timeRemaining;
        state.inMatch = isFighting;
        state.done = doneFlag || isKO;

        string json = JsonUtility.ToJson(state, false);

        try
        {
            File.WriteAllText(filePath, json);
        }
        catch
        {
            Debug.LogWarning("[RL] Write failed");
        }

        // Debug.Log("🧠 RL Export @" + timer.ToString("F2"));
    }

    void OnGameEnds(CharacterInfo winner, CharacterInfo loser)
    {
        matchStarted = false;
        isFighting = false;
        Debug.Log("🛑 RLStateExporter Stopped");
    }
}

[System.Serializable]
public class RLState
{
    public float time;

    public float p1_hp_ratio;
    public float p2_hp_ratio;

    public float hp_ratio_diff;

    public float p1_gauge_ratio;
    public float p2_gauge_ratio;

    public float p1_ultra_gauge_ratio;
    public float p2_ultra_gauge_ratio;

    public float distance;

    public string current_action;
    public bool is_boost_active;

    public string p1_character;
    public string p2_character;

    public bool inMatch;

    public bool done;
}