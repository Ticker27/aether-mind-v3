package com.aetherlab.billiards.ai.visionagent.ai;

import android.os.Handler;
import android.os.Looper;
import android.util.Log;

import com.aetherlab.billiards.ai.visionagent.services.TouchService;

import java.util.Random;

public class AutoPlayEngine {
    private static final String TAG = "AutoPlayEngine";
    private final Handler handler;
    private final Random random;
    private boolean enabled = false;
    private boolean autoAim = true;
    private boolean autoShoot = true;
    private boolean hideGuideline = true;
    private float skillLevel = 0.88f;
    private float thinkDelay = 1.5f;
    private boolean isRunning = false;

    public AutoPlayEngine(Object context) {
        this.handler = new Handler(Looper.getMainLooper());
        this.random = new Random();
    }

    public void setAutoPlayEnabled(boolean enabled) {
        this.enabled = enabled;
        if (enabled) start(); else stop();
    }

    public void setAutoAim(boolean aim) { this.autoAim = aim; }
    public void setAutoShoot(boolean shoot) { this.autoShoot = shoot; }
    public void setHideGuideline(boolean hide) { this.hideGuideline = hide; }
    public void setSkillLevel(float level) { this.skillLevel = level; }
    public void setThinkDelay(float delay) { this.thinkDelay = delay; }

    public void start() {
        if (isRunning) return;
        isRunning = true;
        Log.i(TAG, "AutoPlay engine started");
        runLoop();
    }

    public void stop() {
        isRunning = false;
        Log.i(TAG, "AutoPlay engine stopped");
    }

    public void forceShoot() {
        if (!enabled) return;
        Log.i(TAG, "Force shoot triggered");
        executeShot();
    }

    private void runLoop() {
        if (!isRunning || !enabled) return;

        handler.postDelayed(() -> {
            if (isRunning && enabled && autoShoot) {
                // AI Decision Pipeline:
                // 1. Analyze screen (from native)
                // 2. Calculate best shot
                // 3. Aim (if autoAim)
                // 4. Shoot (if autoShoot)
                executeShot();
            }
            runLoop();
        }, (long)(thinkDelay * 1000));
    }

    private void executeShot() {
        TouchService touch = TouchService.getInstance();
        if (touch == null) {
            Log.w(TAG, "TouchService not available");
            return;
        }

        // Simulate AI shot calculation
        float screenW = 1080f;
        float screenH = 1920f;

        // Cue ball position (center-bottom area)
        float cueX = screenW / 2 + random.nextFloat() * 100 - 50;
        float cueY = screenH * 0.75f + random.nextFloat() * 100;

        // Aim direction (randomized with skill factor)
        float error = (1.0f - skillLevel) * 30f;
        float aimAngle = 270f + random.nextFloat() * error - error/2; // Mostly straight up
        float power = 0.7f + random.nextFloat() * 0.3f;

        // Calculate drag points
        float dragLen = power * 300f;
        float rad = (float)Math.toRadians(aimAngle);
        float endX = cueX - (float)Math.cos(rad) * dragLen;
        float endY = cueY - (float)Math.sin(rad) * dragLen;

        int numPoints = 40;
        float[] xCoords = new float[numPoints];
        float[] yCoords = new float[numPoints];
        long[] timestamps = new long[numPoints];

        for (int i = 0; i < numPoints; i++) {
            float t = (float)i / (numPoints - 1);
            xCoords[i] = cueX + (endX - cueX) * t + random.nextFloat() * 2 - 1;
            yCoords[i] = cueY + (endY - cueY) * t + random.nextFloat() * 2 - 1;
            timestamps[i] = (long)(t * 500);
        }

        Log.i(TAG, String.format("Shot: angle=%.1f, power=%.2f", aimAngle, power));
        touch.executeDrag(xCoords, yCoords, timestamps);
    }
}
