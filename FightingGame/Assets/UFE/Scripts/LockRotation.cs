using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class LockRotation : MonoBehaviour
{
    public Vector3 LockedEulerAngles = Vector3.zero;
	
	// Update is called once per frame
	void Update ()
    {
        transform.eulerAngles = LockedEulerAngles;
	}
}
