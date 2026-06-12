package com.aetherlab.billiards.ai.visionagent;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.provider.Settings;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;
import com.aetherlab.billiards.ai.visionagent.services.AutoPlayService;

public class MainActivity extends Activity {
    private EditText etLicense;
    private Button btnActivate;
    private TextView statusText;

    static { try { System.loadLibrary("aether_agent"); } catch (UnsatisfiedLinkError ignored) {} }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        etLicense = findViewById(R.id.et_license);
        btnActivate = findViewById(R.id.btn_activate);
        statusText = findViewById(R.id.status_text);

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            if (!Settings.canDrawOverlays(this)) {
                startActivity(new Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                    Uri.parse("package:" + getPackageName())));
            }
        }

        btnActivate.setOnClickListener(v -> {
            if (etLicense.getText().toString().trim().length() >= 8) {
                activateAutoPlay();
            } else {
                Toast.makeText(this, "Invalid license key", Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void activateAutoPlay() {
        statusText.setText("● Auto-Play Active");
        Intent serviceIntent = new Intent(this, AutoPlayService.class);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(serviceIntent);
        } else {
            startService(serviceIntent);
        }
        Intent gameIntent = getPackageManager().getLaunchIntentForPackage("com.miniclip.eightballpool");
        if (gameIntent != null) startActivity(gameIntent);
        Toast.makeText(this, "Auto-Play activated! Open 8 Ball Pool", Toast.LENGTH_LONG).show();
        finish();
    }

    public native void nativeInit(String modelPath, int width, int height);
    public native void nativeProcessFrame(long timestamp, int width, int height, byte[] rgbaData);
    public native void nativeSetAutoPlay(boolean aim, boolean shoot, boolean hideGuideline);
    public native void nativeSetSkill(float level);
    public native void nativeSetDelay(float seconds);
    public native void nativeForceShoot();
    public native void nativeDestroy();
}
