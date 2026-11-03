package com.novelrank.app.ui

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

val Ink = Color(0xFF174D40)
val Paper = Color(0xFFF6F4ED)
val Muted = Color(0xFF66736B)
val Warm = Color(0xFF9C5A31)
val Outline = Color(0xFFE1E5DC)

@Composable
fun RankTheme(content: @Composable () -> Unit) {
    MaterialTheme(colorScheme = lightColorScheme(
        primary = Ink, onPrimary = Color.White,
        primaryContainer = Color(0xFFE2ECE4), onPrimaryContainer = Ink,
        background = Paper, onBackground = Color(0xFF202E27),
        surface = Color(0xFFFFFEFA), onSurface = Color(0xFF202E27),
        surfaceVariant = Color(0xFFEEEEE6), onSurfaceVariant = Muted,
        outline = Color(0xFF7D8B81), outlineVariant = Outline,
        secondary = Warm, error = Color(0xFF9B382B),
    ), content = content)
}
