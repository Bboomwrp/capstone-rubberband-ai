using UnityEngine;
using System.Collections;

public class DualAISetup : MonoBehaviour {
    void Start() {
        StartCoroutine(SetupAIControllers());
    }

    IEnumerator SetupAIControllers() {
        // Wait for UFE to initialize
        yield return new WaitUntil(() => UFE.config != null);
        
        // Wait for game to start
        yield return new WaitUntil(() => UFE.gameRunning);

        // Additional wait to ensure controllers are set up
        yield return new WaitForSeconds(0.5f);

        // Try getting controllers through UFE's game engine
        GameObject gameEngine = UFE.gameEngine;
        if (gameEngine == null) {
            Debug.LogError("❌ UFE Game Engine not found!");
            yield break;
        }

        UFEController p1Controller = gameEngine.GetComponent<UFEController>();
        UFEController p2Controller = gameEngine.GetComponent<UFEController>();

        if (p1Controller == null || p2Controller == null) {
            // Try to add controllers if missing
            if (p1Controller == null) {
                p1Controller = gameEngine.AddComponent<UFEController>();
                p1Controller.player = 1;
            }
            
            if (p2Controller == null) {
                p2Controller = gameEngine.AddComponent<UFEController>();
                p2Controller.player = 2;
            }
        }

        // Set both sides to CPU control
        p1Controller.isCPU = true;
        p2Controller.isCPU = true;

        // Add and configure AI components
        SimpleBehaviorAI p1AI = p1Controller.gameObject.GetComponent<SimpleBehaviorAI>();
        if (p1AI == null) {
            p1AI = p1Controller.gameObject.AddComponent<SimpleBehaviorAI>();
        }
        p1AI.player = 1;

        ComplexBehaviorAI p2AI = p2Controller.gameObject.GetComponent<ComplexBehaviorAI>();
        if (p2AI == null) {
            p2AI = p2Controller.gameObject.AddComponent<ComplexBehaviorAI>();
        }
        p2AI.player = 2;

        // Assign AI controllers
        p1Controller.cpuController = p1AI;
        p2Controller.cpuController = p2AI;

        Debug.Log("✅ DualAISetup Loaded! Player1=SimpleBehaviorAI | Player2=ComplexBehaviorAI");
    }
}
