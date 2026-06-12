package com.aetherlab.billiards.ai.visionagent.services;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.Service;
import android.content.Intent;
import android.graphics.PixelFormat;
import android.os.Build;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.view.Gravity;
import android.view.LayoutInflater;
import android.view.MotionEvent;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.CompoundButton;
import android.widget.SeekBar;
import android.widget.Switch;
import android.widget.TextView;
import android.util.Log;

import com.aetherlab.billiards.ai.visionagent.R;
import com.aetherlab.billiards.ai.visionagent.ai.AutoPlayEngine;

public class AutoPlayService extends Service {
    private static final String TAG = "AutoPlayService";
    private WindowManager wm;
    private View bubble, panel;
    private WindowManager.LayoutParams bubbleParams, panelParams;
    private boolean panelVisible = false;
    private AutoPlayEngine engine;
    private Handler mainHandler;

    // Settings
    private boolean autoPlayMaster = false;
    private boolean autoAim = true;
    private boolean autoShoot = true;
    private boolean hideGuideline = true;
    private float skillLevel = 0.88f;
    private float thinkDelay = 1.5f;

    @Override
    public void onCreate() {
        super.onCreate();
        createNotificationChannel();
        startForeground(1, new Notification.Builder(this, "autoplay")
            .setContentTitle("Auto-Play Active").setContentText("AI controlling game")
            .setSmallIcon(android.R.drawable.ic_menu_compass).build());

        wm = (WindowManager) getSystemService(WINDOW_SERVICE);
        mainHandler = new Handler(Looper.getMainLooper());
        engine = new AutoPlayEngine(this);

        createBubble();
        createPanel();
        Log.i(TAG, "AutoPlayService initialized");
    }

    private void createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel c = new NotificationChannel("autoplay", "AutoPlay", NotificationManager.IMPORTANCE_LOW);
            ((NotificationManager) getSystemService(NOTIFICATION_SERVICE)).createNotificationChannel(c);
        }
    }

    private void createBubble() {
        bubble = LayoutInflater.from(this).inflate(R.layout.autoplay_bubble, null);
        bubbleParams = new WindowManager.LayoutParams(
            WindowManager.LayoutParams.WRAP_CONTENT, WindowManager.LayoutParams.WRAP_CONTENT,
            Build.VERSION.SDK_INT >= Build.VERSION_CODES.O ? WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY : WindowManager.LayoutParams.TYPE_PHONE,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE | WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL,
            PixelFormat.TRANSLUCENT);
        bubbleParams.gravity = Gravity.TOP | Gravity.END;
        bubbleParams.x = 50; bubbleParams.y = 300;

        bubble.setOnTouchListener(new View.OnTouchListener() {
            float dx, dy; int ix, iy;
            @Override public boolean onTouch(View v, MotionEvent e) {
                switch (e.getAction()) {
                    case MotionEvent.ACTION_DOWN:
                        ix = bubbleParams.x; iy = bubbleParams.y;
                        dx = e.getRawX(); dy = e.getRawY();
                        return true;
                    case MotionEvent.ACTION_MOVE:
                        bubbleParams.x = ix + (int)(e.getRawX() - dx);
                        bubbleParams.y = iy + (int)(e.getRawY() - dy);
                        wm.updateViewLayout(bubble, bubbleParams);
                        return true;
                    case MotionEvent.ACTION_UP:
                        if (Math.abs(e.getRawX()-dx) < 5 && Math.abs(e.getRawY()-dy) < 5) togglePanel();
                        return true;
                }
                return false;
            }
        });
        wm.addView(bubble, bubbleParams);
    }

    private void createPanel() {
        panel = LayoutInflater.from(this).inflate(R.layout.autoplay_panel, null);
        panelParams = new WindowManager.LayoutParams(
            280, WindowManager.LayoutParams.WRAP_CONTENT,
            Build.VERSION.SDK_INT >= Build.VERSION_CODES.O ? WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY : WindowManager.LayoutParams.TYPE_PHONE,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
            PixelFormat.TRANSLUCENT);
        panelParams.gravity = Gravity.CENTER;

        // Master Switch
        ((Switch) panel.findViewById(R.id.sw_autoplay_master)).setOnCheckedChangeListener((b, on) -> {
            autoPlayMaster = on;
            engine.setAutoPlayEnabled(on);
            updateEngineSettings();
        });

        // Auto-Aim Switch
        ((Switch) panel.findViewById(R.id.sw_auto_aim)).setOnCheckedChangeListener((b, on) -> {
            autoAim = on;
            updateEngineSettings();
        });

        // Auto-Shoot Switch
        ((Switch) panel.findViewById(R.id.sw_auto_shoot)).setOnCheckedChangeListener((b, on) -> {
            autoShoot = on;
            updateEngineSettings();
        });

        // Hide Guideline Switch
        ((Switch) panel.findViewById(R.id.sw_hide_guideline)).setOnCheckedChangeListener((b, on) -> {
            hideGuideline = on;
            updateEngineSettings();
        });

        // Skill Slider
        ((SeekBar) panel.findViewById(R.id.sb_skill)).setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override public void onProgressChanged(SeekBar s, int p, boolean u) {
                skillLevel = p / 100.0f;
                ((TextView) panel.findViewById(R.id.tv_skill)).setText("AI Skill: " + p + "%");
                updateEngineSettings();
            }
            @Override public void onStartTrackingTouch(SeekBar s) {}
            @Override public void onStopTrackingTouch(SeekBar s) {}
        });

        // Delay Slider
        ((SeekBar) panel.findViewById(R.id.sb_delay)).setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override public void onProgressChanged(SeekBar s, int p, boolean u) {
                thinkDelay = p / 10.0f;
                ((TextView) panel.findViewById(R.id.tv_delay)).setText("Think Delay: " + thinkDelay + "s");
                updateEngineSettings();
            }
            @Override public void onStartTrackingTouch(SeekBar s) {}
            @Override public void onStopTrackingTouch(SeekBar s) {}
        });

        // Launch Game Button
        panel.findViewById(R.id.btn_launch_game).setOnClickListener(v -> {
            Intent i = getPackageManager().getLaunchIntentForPackage("com.miniclip.eightballpool");
            if (i != null) { i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK); startActivity(i); }
        });

        // Force Shoot Button
        panel.findViewById(R.id.btn_force_shoot).setOnClickListener(v -> {
            engine.forceShoot();
        });

        // Hide Button
        panel.findViewById(R.id.btn_hide).setOnClickListener(v -> hidePanel());
    }

    private void updateEngineSettings() {
        engine.setAutoAim(autoPlayMaster && autoAim);
        engine.setAutoShoot(autoPlayMaster && autoShoot);
        engine.setHideGuideline(autoPlayMaster && hideGuideline);
        engine.setSkillLevel(skillLevel);
        engine.setThinkDelay(thinkDelay);
    }

    private void togglePanel() { if (panelVisible) hidePanel(); else showPanel(); }
    private void showPanel() { if (!panelVisible) { wm.addView(panel, panelParams); panelVisible = true; } }
    private void hidePanel() { if (panelVisible) { wm.removeView(panel); panelVisible = false; } }

    @Override public int onStartCommand(Intent i, int f, int id) { return START_STICKY; }
    @Override public IBinder onBind(Intent i) { return null; }
    @Override public void onDestroy() {
        if (engine != null) engine.stop();
        if (bubble != null) wm.removeView(bubble);
        if (panelVisible) wm.removeView(panel);
        super.onDestroy();
    }
}
