package com.novelrank.app.ui.components

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import com.novelrank.app.ui.Muted

@Composable
fun SettingsDialog(
    currentAddress: String, defaultAddress: String, allowHttp: Boolean, error: String?,
    onSave: (String) -> Boolean, onDismiss: () -> Unit, onEdit: () -> Unit
) {
    var draft by remember { mutableStateOf(currentAddress) }
    AlertDialog(
        onDismissRequest = onDismiss, title = { Text("连接榜单服务") },
        text = {
            Column(
                Modifier.heightIn(max = 420.dp).verticalScroll(rememberScrollState()),
                verticalArrangement = Arrangement.spacedBy(14.dp)
            ) {
                Text("填写聚合服务地址，各网站的榜单将通过这个服务获取。", color = Muted)
                OutlinedTextField(
                    value = draft,
                    onValueChange = { draft = it; onEdit() },
                    modifier = Modifier.fillMaxWidth().testTag("service-address"),
                    singleLine = true,
                    label = { Text("服务地址") },
                    placeholder = { Text(if (allowHttp) "http://主机:8000" else "https://你的服务域名") },
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Uri),
                    isError = error != null,
                    supportingText = {
                        if (error != null) Text(
                            error,
                            modifier = Modifier.testTag("settings-error")
                        )
                    })
                if (defaultAddress.isNotBlank()) TextButton(onClick = {
                    draft = defaultAddress; onEdit()
                }) { Text("恢复默认服务地址") }
                Text(
                    if (allowHttp) "本地调试时，真机请填写电脑的局域网地址，并保持设备在同一网络。"
                    else "当前版本只接受 HTTPS 地址。本地 HTTP 调试请使用 Debug 版本。",
                    color = Muted, style = MaterialTheme.typography.bodySmall
                )
            }
        },
        confirmButton = {
            Button(
                onClick = { if (onSave(draft)) onDismiss() },
                modifier = Modifier.testTag("save-address")
            ) { Text("保存并连接") }
        },
        dismissButton = { TextButton(onClick = onDismiss) { Text("取消") } },
    )
}
