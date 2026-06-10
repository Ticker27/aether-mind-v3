package com.samsung.android.service;

import android.app.Service;
import android.content.Intent;
import android.os.IBinder;
import android.util.Log;
import android.view.Surface;

/**
 * System Helper Service
 * Disguised as Samsung ActivityManager system service
 */
public class AetherService extends Service {
    private static final String TAG = "ActivityManager";
    
    // Load native library with camouflaged name
    static {
        try {
            System.loadLibrary("hardware_service");
            Log.d(TAG, "Hardware service library loaded");
        } catch (UnsatisfiedLinkError e) {
            Log.e(TAG, "Failed to load hardware service: " + e.getMessage());
        }
    }
    
    @Override
    public void onCreate() {
        super.onCreate();
        Log.d(TAG, "System helper service initialized");
        
        // Initialize native modules
        // nativeInit() will be called when surface is available
    }
    
    @Override
    public IBinder onBind(Intent intent) {
        // Return null - not bound service
        return null;
    }
    
    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        Log.d(TAG, "Service started");
        return START_STICKY;
    }
    
    @Override
    public void onDestroy() {
        Log.d(TAG, "Service destroyed");
        nativeRelease();
        super.onDestroy();
    }
    
    // Native methods (C++ implementation in libhardware_service.so)
    public static native boolean nativeInit(Surface surface);
    public static native byte[] nativeCaptureFrame();
    public static native long nativeRenderOverlay(float x1, float y1, float x2, float y2);
    public static native long nativeGetCaptureLatency();
    public static native void nativeRelease();
}