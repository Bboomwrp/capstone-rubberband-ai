using UnityEngine;
using System.Collections.Generic;

public class ComplexBehaviorAI : AbstractInputController {
    protected float timeLastDecision = float.NegativeInfinity;

    private List<MoveInfo> closeRangeMoves = new List<MoveInfo>();
    private List<MoveInfo> midRangeMoves = new List<MoveInfo>();
    private List<MoveInfo> longRangeMoves = new List<MoveInfo>();
    private List<MoveInfo> defensiveMoves = new List<MoveInfo>();

    private bool movesInitialized = false;

    public override void Initialize(IEnumerable<InputReferences> inputs, int bufferSize){
        this.timeLastDecision = float.NegativeInfinity;
        base.Initialize(inputs, bufferSize);
    }

    public override void DoUpdate(){
        if (this.inputReferences != null){
            float currentTime = Time.realtimeSinceStartup;
            if (this.timeLastDecision < 0f) this.timeLastDecision = currentTime;

            this.currentFrameInputs.Clear();

            if (currentTime - this.timeLastDecision >= 0.1f){
                this.timeLastDecision = currentTime;
                foreach (InputReferences input in this.inputReferences)
                    this.currentFrameInputs[input] = this.ReadInput(input);
            } else {
                foreach (InputReferences input in this.inputReferences)
                    this.currentFrameInputs[input] = InputEvents.Default;
            }
        }
    }

    public override InputEvents ReadInput(InputReferences inputReference){
        ControlsScript self = UFE.GetControlsScript(this.player);
        if (self == null) return InputEvents.Default;

        ControlsScript opponent = self.opControlsScript;
        if (opponent == null) return InputEvents.Default;

        // โหลด moves แค่ครั้งเดียว
        if (!movesInitialized && self.myInfo != null){
            ClassifyMoves(self.myInfo.moves);
            movesInitialized = true;
        }

        float dx = opponent.transform.position.x - self.transform.position.x;
        float dist = Mathf.Abs(dx);
        float myHP = self.myInfo.currentLifePoints;
        float enemyHP = opponent.myInfo.currentLifePoints;
        MoveInfo chosenMove = null;

        // ---------------- Rule-based Decision ----------------
        if (myHP < enemyHP * 0.5f && defensiveMoves.Count > 0){
            chosenMove = defensiveMoves[Random.Range(0, defensiveMoves.Count)];
        }
        else if (dist < 2.5f && closeRangeMoves.Count > 0){
            chosenMove = closeRangeMoves[Random.Range(0, closeRangeMoves.Count)];
        }
        else if (dist < 5f && midRangeMoves.Count > 0){
            chosenMove = midRangeMoves[Random.Range(0, midRangeMoves.Count)];
        }
        else if (dist >= 5f && longRangeMoves.Count > 0){
            chosenMove = longRangeMoves[Random.Range(0, longRangeMoves.Count)];
        }

        if (chosenMove == null && closeRangeMoves.Count > 0)
            chosenMove = closeRangeMoves[Random.Range(0, closeRangeMoves.Count)];

        return ExecuteMove(inputReference, self, chosenMove, dx);
    }

    private void ClassifyMoves(MoveSetData[] moveSets){
        foreach (MoveSetData moveSet in moveSets){
            if (moveSet == null) continue;

            // อ่าน MoveInfo ภายใน MoveSetData
            MoveInfo[] allMoves = moveSet.attackMoves;
            if (allMoves == null || allMoves.Length == 0) continue;

            foreach (MoveInfo move in allMoves){
                if (move == null || string.IsNullOrEmpty(move.moveName)) continue;

                string name = move.moveName.ToLower();

                // จัดหมวดตามชื่อท่า
                if (name.Contains("punch") || name.Contains("kick") || name.Contains("attack"))
                    closeRangeMoves.Add(move);
                else if (name.Contains("hadou") || name.Contains("fire") || name.Contains("wave"))
                    longRangeMoves.Add(move);
                else if (name.Contains("dash") || name.Contains("special"))
                    midRangeMoves.Add(move);
                else if (name.Contains("block") || name.Contains("guard"))
                    defensiveMoves.Add(move);
                else
                    closeRangeMoves.Add(move);
            }
        }

        Debug.Log("✅ ComplexBehaviorAI: Loaded moves - Close:" + closeRangeMoves.Count +
            " Mid:" + midRangeMoves.Count + " Long:" + longRangeMoves.Count + " Def:" + defensiveMoves.Count);
    }

    private InputEvents ExecuteMove(InputReferences inputRef, ControlsScript self, MoveInfo move, float dx){
        if (move == null) return InputEvents.Default;

        // ทิศทางเข้าหาศัตรู
        if (inputRef.inputType == InputType.HorizontalAxis){
            return new InputEvents(Mathf.Sign(dx));
        }

        // กระโดด (สุ่ม)
        if (inputRef.inputType == InputType.VerticalAxis){
            if (Random.value < 0.1f) return new InputEvents(1f);
        }

        // ปุ่มโจมตีสุ่ม
        if (inputRef.engineRelatedButton == ButtonPress.Button1 && Random.value < 0.5f) return new InputEvents(true);
        if (inputRef.engineRelatedButton == ButtonPress.Button2 && Random.value < 0.5f) return new InputEvents(true);
        if (inputRef.engineRelatedButton == ButtonPress.Button3 && Random.value < 0.3f) return new InputEvents(true);
        if (inputRef.engineRelatedButton == ButtonPress.Button4 && Random.value < 0.2f) return new InputEvents(true);

        return InputEvents.Default;
    }
}
