package com.aetherlab.billiards.ai.visionagent.services;

import android.accessibilityservice.AccessibilityService;
import android.accessibilityservice.GestureDescription;
import android.graphics.Path;
import android.util.Log;
import android.view.accessibility.AccessibilityEvent;

public class TouchService extends AccessibilityService {
    private static final String TAG = "AutoPlayTouch";
    private static TouchService instance;
    public static TouchService getInstance() { return instance; }

    @Override public void onServiceConnected() { super.onServiceConnected(); instance = this; Log.i(TAG, "TouchService ready"); }
    @Override public void onAccessibilityEvent(AccessibilityEvent e) {}
    @Override public void onInterrupt() {}
    @Override public void onDestroy() { instance = null; super.onDestroy(); }

    public boolean executeDrag(float[] x, float[] y, long[] ts) {
        if (x == null || y == null || ts == null || x.length < 2) return false;
        Path path = new Path(); path.moveTo(x[0], y[0]);
        GestureDescription.Builder builder = new GestureDescription.Builder();
        long cum = 0;
        for (int i = 1; i < x.length; i++) {
            path.lineTo(x[i], y[i]);
            long dur = Math.max(1, ts[i] - ts[i-1]);
            builder.addStroke(new GestureDescription.StrokeDescription(path, cum, dur));
            cum += dur;
        }
        return dispatchGesture(builder.build(), null, null);
    }

    public boolean executeTap(float x, float y) {
        Path path = new Path(); path.moveTo(x, y);
        GestureDescription.Builder builder = new GestureDescription.Builder();
        builder.addStroke(new GestureDescription.StrokeDescription(path, 0, 1));
        return dispatchGesture(builder.build(), null, null);
    }
}
