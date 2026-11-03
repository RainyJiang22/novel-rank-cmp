package com.novelrank.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.runtime.remember
import com.novelrank.app.data.AndroidSettingsStore
import com.novelrank.app.data.ClientEnvironment
import com.novelrank.app.data.CLOUD_SERVICE_ADDRESS

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            val environment = remember {
                ClientEnvironment(AndroidSettingsStore(applicationContext), CLOUD_SERVICE_ADDRESS, allowHttp = BuildConfig.DEBUG)
            }
            App(environment)
        }
    }
}
