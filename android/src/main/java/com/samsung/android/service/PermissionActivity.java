package com.samsung.android.service;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;

/**
 * Permission Activity for MediaProjection
 * 
 * Handles screen capture permission request
 * This activity is invisible (Theme.NoDisplay)
 */
public class PermissionActivity extends Activity {
    private static final String TAG = "PermissionActivity";
    private static final int REQUEST_MEDIA_PROJECTION = 1001;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        Log.d(TAG, "Permission activity created");
        
        // Request media projection permission
        Intent intent = new Intent(Intent.ACTION_MAIN);
        intent.setClassName("com.android.systemui", "com.android.systemui.media.MediaProjectionPermissionActivity");
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        startActivityForResult(intent, REQUEST_MEDIA_PROJECTION);
    }
    
    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        
        if (requestCode == REQUEST_MEDIA_PROJECTION) {
            if (resultCode == RESULT_OK) {
                Log.d(TAG, "Media projection permission granted");
                // Store result data for service to use
                if (data != null) {
                    // Service will retrieve this data
                }
            } else {
                Log.w(TAG, "Media projection permission denied");
            }
            finish();
        }
    }
}