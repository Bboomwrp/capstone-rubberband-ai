using UnityEngine;
using System.Collections.Generic;

public class SimpleBehaviorAI : AbstractInputController {
    protected float timeLastDecision = float.NegativeInfinity;

    public override void Initialize(IEnumerable<InputReferences> inputs, int bufferSize){
        this.timeLastDecision = float.NegativeInfinity;
        base.Initialize(inputs, bufferSize);
    }

    public override void DoUpdate(){
        if (this.inputReferences != null){
            float currentTime = Time.realtimeSinceStartup;
            if (this.timeLastDecision < 0f) this.timeLastDecision = currentTime;

            this.currentFrameInputs.Clear();
            if (currentTime - this.timeLastDecision >= UFE.config.aiOptions.inputFrequency){
                this.timeLastDecision = currentTime;

                foreach (InputReferences input in this.inputReferences) {
                    this.currentFrameInputs[input] = this.ReadInput(input);
                }
            } else {
                foreach (InputReferences input in this.inputReferences) {
                    this.currentFrameInputs[input] = InputEvents.Default;
                }
            }
        }
    }

    public override InputEvents ReadInput(InputReferences inputReference){
        ControlsScript self = UFE.GetControlsScript(this.player);
        if (self == null) return InputEvents.Default;

        ControlsScript opponent = self.opControlsScript;
        if (opponent == null) return InputEvents.Default;

        float dx = opponent.transform.position.x - self.transform.position.x;
        bool isOpponentDown = opponent.currentState == PossibleStates.Down;
        int distance = Mathf.RoundToInt(100f * Mathf.Clamp01(self.normalizedDistance));

        AIDistanceBehaviour behaviour = null;
        foreach (AIDistanceBehaviour b in UFE.config.aiOptions.distanceBehaviour){
            if (b != null && distance >= b.proximityRangeBegins && distance <= b.proximityRangeEnds){
                behaviour = b;
                break;
            }
        }
        if (behaviour == null) return InputEvents.Default;


        if (inputReference.inputType == InputType.HorizontalAxis) {
            float axis = Mathf.Sign(dx) * (Random.Range(0f, 1f) < 0.7f ? 1f : -1f);
            return new InputEvents(axis);
        } else if (inputReference.inputType == InputType.VerticalAxis) {
            float axis = (Random.Range(0f, 1f) < 0.2f ? 1f : 0f);
            return new InputEvents(axis);
        } else {
            if (!UFE.config.aiOptions.attackWhenEnemyIsDown && isOpponentDown)
                return InputEvents.Default;

            if (inputReference.engineRelatedButton == ButtonPress.Button1 ||
                inputReference.engineRelatedButton == ButtonPress.Button2 ||
                inputReference.engineRelatedButton == ButtonPress.Button3)
            {
                return new InputEvents(Random.Range(0f, 1f) < 0.5f);
            }
        }

        return InputEvents.Default;
    }
}
