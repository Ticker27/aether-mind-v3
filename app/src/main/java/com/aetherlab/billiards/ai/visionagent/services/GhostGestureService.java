package com.aetherlab.billiards.ai.visionagent.services;

import android.accessibilityservice.AccessibilityService;
import android.content.Intent;
import android.view.accessibility.AccessibilityEvent;

public class GhostGestureService extends AccessibilityService {
    private int fingerCount = 0;
    private long touchStart = 0;

    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {
        if (event.getEventType() == AccessibilityEvent.TYPE_TOUCH_INTERACTION_START) {
            fingerCount++;
            touchStart = System.currentTimeMillis();
        } else if (event.getEventType() == AccessibilityEvent.TYPE_TOUCH_INTERACTION_END) {
            long duration = System.currentTimeMillis() - touchStart;
            if (fingerCount >= 3 && duration < 500) {
                Intent i = new Intent("com.aetherlab.TOGGLE_PANEL");
                sendBroadcast(i);
            }
            fingerCount = 0;
        }
    }

    @Override
    public void onInterrupt() {}
}
