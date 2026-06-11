package com.samsung.android.service;

import android.app.Activity;
import android.os.Bundle;
import android.util.Log;

/**
 * Main Activity (hidden)
 * 
 * Exists only for APK structure
 * Never shown to user
 */
public class MainActivity extends Activity {
    private static final String TAG = "MainActivity";
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        Log.d(TAG, "Main activity created (invisible)");
        finish();
    }
}