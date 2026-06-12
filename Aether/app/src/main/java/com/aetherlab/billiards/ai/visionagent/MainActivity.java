package com.aetherlab.billiards.ai.visionagent;

import android.app.Activity;
import android.content.Intent;
import android.media.projection.MediaProjectionManager;
import android.os.Bundle;
import android.provider.Settings;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

public class MainActivity extends Activity {
    private static final int REQUEST_MEDIA_PROJECTION = 1001;
    private MediaProjectionManager projectionManager;
    private JNIBridge jniBridge;
    private TextView statusText;
    private Button btnStart, btnStop;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        statusText = findViewById(R.id.status_text);
        btnStart = findViewById(R.id.btn_start);
        btnStop = findViewById(R.id.btn_stop);

        projectionManager = (MediaProjectionManager) getSystemService(MEDIA_PROJECTION_SERVICE);
        jniBridge = new JNIBridge();

        try {
            System.loadLibrary("aether_agent");
        } catch (UnsatisfiedLinkError e) {
            Toast.makeText(this, "Native library failed to load", Toast.LENGTH_LONG).show();
            finish();
        }

        btnStart.setOnClickListener(v -> {
            if (!isAccessibilityEnabled()) {
                startActivity(new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS));
                Toast.makeText(this, "Enable TouchService in Accessibility settings", Toast.LENGTH_LONG).show();
                return;
            }
            startActivityForResult(
                projectionManager.createScreenCaptureIntent(),
                REQUEST_MEDIA_PROJECTION
            );
        });

        btnStop.setOnClickListener(v -> {
            jniBridge.stopCapture();
            statusText.setText("● Agent Stopped");
            btnStart.setEnabled(true);
            btnStop.setEnabled(false);
        });
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQUEST_MEDIA_PROJECTION && resultCode == RESULT_OK) {
            jniBridge.startCapture(
                projectionManager.getMediaProjection(resultCode, data),
                1080, 1920, getResources().getDisplayMetrics().densityDpi
            );
            statusText.setText("● Agent Active");
            btnStart.setEnabled(false);
            btnStop.setEnabled(true);
        }
    }

    private boolean isAccessibilityEnabled() {
        String service = getPackageName() + "/" + TouchService.class.getCanonicalName();
        int enabled = Settings.Secure.getInt(getContentResolver(), Settings.Secure.ACCESSIBILITY_ENABLED, 0);
        if (enabled == 1) {
            String services = Settings.Secure.getString(getContentResolver(), Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES);
            return services != null && services.contains(service);
        }
        return false;
    }
}
