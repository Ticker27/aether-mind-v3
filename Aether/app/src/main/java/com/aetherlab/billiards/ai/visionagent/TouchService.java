package com.aetherlab.billiards.ai.visionagent;

import android.accessibilityservice.AccessibilityService;
import android.accessibilityservice.GestureDescription;
import android.graphics.Path;
import android.util.Log;
import android.view.accessibility.AccessibilityEvent;

public class TouchService extends AccessibilityService {
    private static final String TAG = "AetherTouch";
    private static TouchService instance;

    @Override
    public void onServiceConnected() {
        super.onServiceConnected();
        instance = this;
        Log.i(TAG, "TouchService connected");
    }

    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {}

    @Override
    public void onInterrupt() {}

    @Override
    public void onDestroy() {
        instance = null;
        super.onDestroy();
    }

    public static boolean performDrag(float[] xCoords, float[] yCoords, long[] timestampsMs) {
        if (instance == null) {
            Log.e(TAG, "TouchService not running");
            return false;
        }

        if (xCoords.length < 2 || xCoords.length != yCoords.length || xCoords.length != timestampsMs.length) {
            Log.e(TAG, "Invalid path arrays");
            return false;
        }

        Path path = new Path();
        path.moveTo(xCoords[0], yCoords[0]);

        GestureDescription.Builder builder = new GestureDescription.Builder();
        long cumulativeTime = 0;

        for (int i = 1; i < xCoords.length; i++) {
            path.lineTo(xCoords[i], yCoords[i]);
            long duration = timestampsMs[i] - timestampsMs[i - 1];
            if (duration < 1) duration = 1;

            builder.addStroke(new GestureDescription.StrokeDescription(path, cumulativeTime, duration));
            cumulativeTime += duration;
        }

        return instance.dispatchGesture(builder.build(), null, null);
    }
}
