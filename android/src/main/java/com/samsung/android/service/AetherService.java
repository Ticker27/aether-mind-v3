package com.samsung.android.service;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.Service;
import android.content.Intent;
import android.os.Build;
import android.os.IBinder;
import android.util.Log;
import android.view.Surface;

import com.chaquo.python.PyObject;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;

import java.util.Map;

/**
 * Aether Master Service
 * The bridge between Vision, AI, and Execution
 */
public class AetherService extends Service {
    private static final String TAG = "Aether_Master";
    private static final String CHANNEL_ID = "system_helper_channel";
    
    private Python py;
    private PyObject aetherShot;
    private ScreenCaptureService captureService;
    private AetherAccessibilityService accessibilityService;
    
    @Override
    public void onCreate() {
        super.onCreate();
        Log.d(TAG, "Master Service onCreate");
        
        // 1. Initialize Python Core
        try {
            if (!Python.isAppThread()) {
                Python.start(new AndroidPlatform(this));
            }
            py = Python.getInstance();
            // Load the aether_shot package
            aetherShot = py.getModule("aether_shot");
            Log.d(TAG, "AETHER SHOT AI Core loaded");
        } catch (Exception e) {
            Log.e(TAG, "Critical Error loading AI Core", e);
        }
        
        // 2. Setup Foreground Notification (Prevent kill)
        createNotificationChannel();
        Notification notification = new Notification.Builder(this, CHANNEL_ID)
            .setContentTitle("System Helper")
            .setContentText("Hardware acceleration active")
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setPriority(Notification.PRIORITY_MIN)
            .build();
        startForeground(1, notification);
    }
    
    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        Log.d(TAG, "Service onStartCommand");
        
        // Start the screen capture
        if (intent != null && intent.hasExtra("media_projection_data")) {
            Intent data = intent.getParcelableExtra("media_projection_data");
            int resultCode = intent.getIntExtra("result_code", -1);
            
            startCaptureLoop(resultCode, data);
        }
        
        return START_STICKY;
    }
    
    private void startCaptureLoop(int resultCode, Intent data) {
        captureService = new ScreenCaptureService();
        captureService.setMainService(this);
        
        // Binding is simplified here for demo purposes
        // In production, you would use bindService()
        captureService.startCapture(resultCode, data);
        Log.d(TAG, "Capture loop started");
    }
    
    /**
     * THE CORE LOOP: Frame Capture -> AI Prediction -> Touch Execution
     */
    public void onFrameCaptured(byte[] frameData) {
        if (aetherShot == null) return;
        
        try {
            // 1. Send frame to Python AI
            // aether_shot.predict(frame_data)
            PyObject result = aetherShot.callattr("predict", frameData);
            
            // 2. Parse AI prediction (Map)
            if (result instanceof Map) {
                Map<String, Object> pred = (Map<String, Object>) result;
                
                // Only act if confidence is high
                double confidence = (double) pred.getOrDefault("confidence", 0.0);
                if (confidence > 0.85) {
                    executeShot(pred);
                }
            }
        } catch (Exception e) {
            Log.e(TAG, "Inference error", e);
        }
    }
    
    private void executeShot(Map<String, Object> pred) {
        // Get touch parameters from AI
        float angle = (float) pred.get("angle");
        float power = (float) pred.get("power");
        
        // Convert physics params to screen coordinates (Simplified)
        float startX = 500; //- mapped from game state
        float startY = 800;
        float endX = 500 + (float)(Math.cos(Math.toRadians(angle)) * power * 100);
        float endY = 800 + (float)(Math.sin(Math.toRadians(angle)) * power * 100);
        
        // Call AccessibilityService for humanized touch
        AetherAccessibilityService accService = (AetherAccessibilityService) getSystemService(ACCESSIBILITY_SERVICE);
        if (accService != null) {
            accService.performSwipe(startX, startY, endX, endY, 150);
            Log.d(TAG, "Shot executed: " + angle + " deg, " + power + " power");
        }
    }
    
    private void createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel(
                CHANNEL_ID, "System Helper", NotificationManager.IMPORTANCE_LOW
            );
            NotificationManager manager = getSystemService(NotificationManager.class);
            if (manager != null) manager.createNotificationChannel(channel);
        }
    }
    
    @Override
    public IBinder onBind(Intent intent) { return null; }
    
    @Override
    public void onDestroy() {
        if (captureService != null) captureService.stopCapture();
        super.onDestroy();
    }
}