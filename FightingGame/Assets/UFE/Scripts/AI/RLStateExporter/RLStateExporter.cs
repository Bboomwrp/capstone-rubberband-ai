using UnityEngine;
using System.Collections;
using System.IO;

public class RLStateExporter : MonoBehaviour
{
    private ControlsScript p1;
    private ControlsScript p2;

    private string filePath;

    private bool matchStarted = false;

    private float interval = 1f;
    private float lastTime = 0f;
    private float roundStartTime;
    private float roundDuration = 99f;

    private bool isFighting = false;
    private bool roundJustEnded = false;
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

        roundStartTime=Time.time;

        filePath = Application.persistentDataPath + "/rl_state.json";

        Debug.Log("🧠 RLStateExporter Started: " + filePath);

        matchStarted = true;
        lastTime = Time.time;
    }

    void OnRoundBegin(int round)
    {
        isFighting = true;
        roundStartTime = Time.time;
        doneSent = false;

        Debug.Log("🔥 Round Started: " + round);
    }

    void OnRoundEnd(CharacterInfo winner, CharacterInfo loser)
    {
        isFighting = false;
        roundJustEnded = true;

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

            Debug.Log("✅ DONE (HP KO DETECT)");
            return;
        }

        if (roundJustEnded && !doneSent)
        {
            ExportState(true);
            doneSent = true;
            roundJustEnded = false;

            Debug.Log("✅ DONE (EVENT)");
            return;
        }

        if (!isFighting) return;

        if (Time.time - lastTime >= interval)
        {
            lastTime = Time.time;
            ExportState(false);
        }

        if (UFE.GetTimer() >= UFE.config.roundOptions.timer) return;
    }

    void ExportState(bool doneFlag)
    {
        float p1HP = p1.myInfo.currentLifePoints;
        float p2HP = p2.myInfo.currentLifePoints;
        float maxHP = Mathf.Max(p1.myInfo.lifePoints, p2.myInfo.lifePoints);

        if (p1HP <= 0 || p2HP <= 0)
        {
            Debug.Log("⚠️ KO DETECTED | doneSent=" + doneSent + " | isFighting=" + isFighting);
        }

        float hpDiff = (p1HP - p2HP) / maxHP;
        float hpRatio = (p1HP + p2HP) / (2f * maxHP);

        float p1Gauge = p1.myInfo.currentGaugePoints;
        float p2Gauge = p2.myInfo.currentGaugePoints;

        float distance = Mathf.Abs(
            p1.transform.position.x - p2.transform.position.x
        );

        float timer = UFE.GetTimer();
        float maxTime = UFE.config.roundOptions.timer;

        float timeRemaining = timer / maxTime;
        timeRemaining = Mathf.Clamp01(timeRemaining);

        bool isKO = p1HP <= 0 || p2HP <= 0;

        RLState state = new RLState();
        state.hp_diff = hpDiff;
        state.hp_ratio = hpRatio;
        state.p1_hp = p1HP;
        state.p2_hp = p2HP;
        state.p1_gauge = p1Gauge;
        state.p2_gauge = p2Gauge;
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

    public float p1_hp;
    public float p2_hp;

    public float hp_diff;
    public float hp_ratio;

    public float p1_gauge;
    public float p2_gauge;

    public float distance;

    public bool inMatch;

    public bool done;
}