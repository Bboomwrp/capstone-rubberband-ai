using UnityEngine;
using System.Collections;
using System.IO;

public class BattleLogger : MonoBehaviour {

    private ControlsScript p1;
    private ControlsScript p2;

    private string folderPath;
    private string filePath;

    private bool matchStarted = false;
    private float logInterval = 1f; // 🔥 sync RL (1 sec)
    private float lastLogTime = 0f;

    private int roundNumber = 1;

    void OnEnable() {
        UFE.OnGameBegin += OnGameBegin;
        UFE.OnRoundEnds += OnRoundEnd;
        UFE.OnGameEnds += OnGameEnds;
    }

    void OnDisable() {
        UFE.OnGameBegin -= OnGameBegin;
        UFE.OnRoundEnds -= OnRoundEnd;
        UFE.OnGameEnds -= OnGameEnds;
    }

    void OnGameBegin(CharacterInfo p1Info, CharacterInfo p2Info, StageOptions stage) {

        p1 = UFE.GetControlsScript(1);
        p2 = UFE.GetControlsScript(2);

        folderPath = Application.persistentDataPath + "/BattleLogs";
        if (!Directory.Exists(folderPath)) Directory.CreateDirectory(folderPath);

        roundNumber = 1;
        CreateNewRoundFile();

        Debug.Log("📘 BattleLogger Started");

        matchStarted = true;
    }

    void CreateNewRoundFile() {
        string timeName = System.DateTime.Now.ToString("yyyyMMdd_HHmmss");
        filePath = folderPath + "/round_" + roundNumber + "_" + timeName + ".csv";

        File.WriteAllText(
            filePath,
            "time,p1HP,p2HP,hpDiff,hpRatio,distance,p1Gauge,p2Gauge,p1Move,p2Move,event\n"
        );

        Debug.Log("📝 New Round File: " + filePath);
    }

    void Update() {
        if (!matchStarted) return;
        if (p1 == null || p2 == null) return;

        if (Time.time - lastLogTime >= logInterval) {
            lastLogTime = Time.time;

            LogFrame();
        }
    }

    void LogFrame() {

        float p1HP = p1.myInfo.currentLifePoints;
        float p2HP = p2.myInfo.currentLifePoints;

        float maxHP = p1.myInfo.lifePoints;

        float hpDiff = (p1HP - p2HP) / maxHP;
        float hpRatio = (p1HP + p2HP) / (2f * maxHP);

        float distance = Mathf.Abs(
            p1.transform.position.x - p2.transform.position.x
        );

        float p1Gauge = p1.myInfo.currentGaugePoints;
        float p2Gauge = p2.myInfo.currentGaugePoints;

        string p1Move = (p1.currentMove != null) ? p1.currentMove.moveName : "None";
        string p2Move = (p2.currentMove != null) ? p2.currentMove.moveName : "None";

        float timer = UFE.GetTimer();
        float maxTime = UFE.config.roundOptions.timer;

        float timeRemaining = timer / maxTime;
        timeRemaining = Mathf.Clamp01(timeRemaining);

        string line =
            timeRemaining + "," +
            p1HP + "," +
            p2HP + "," +
            hpDiff.ToString("F3") + "," +
            hpRatio.ToString("F3") + "," +
            distance.ToString("F2") + "," +
            p1Gauge + "," +
            p2Gauge + "," +
            p1Move + "," +
            p2Move + "," +
            "none\n";

        File.AppendAllText(filePath, line);
    }

    void OnRoundEnd(CharacterInfo winner, CharacterInfo loser) {
        if (string.IsNullOrEmpty(filePath)) return;

        string winName = (winner != null) ? winner.characterName : "Unknown";

        File.AppendAllText(
            filePath,
            "0,0,0,0,0,0,0,0,None,None,ROUND_END:" + winName + "\n"
        );

        Debug.Log("🟦 Round End logged: " + winName);

        // 🔥 แยกไฟล์ round ใหม่
        roundNumber++;
        CreateNewRoundFile();
    }

    void OnGameEnds(CharacterInfo winner, CharacterInfo loser) {
        string result = (winner != null) ? winner.characterName : "FORCE_END";

        File.AppendAllText(
            filePath,
            "0,0,0,0,0,0,0,0,None,None,MATCH_END:" + result + "\n"
        );

        Debug.Log("🏁 Match End logged: " + result);

        matchStarted = false;
    }
}