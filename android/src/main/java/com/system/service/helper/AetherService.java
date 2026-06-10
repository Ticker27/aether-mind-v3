package com.samsung.android.service;

import android.app.Service;
import android.content.Intent;
import android.os.IBinder;

public class AetherService extends Service {
    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        // Service running in background
        return START_STICKY;
    }
}