package com.novelrank.app.ui.components

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.semantics.selected
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.novelrank.app.model.Source
import com.novelrank.app.ui.Ink
import com.novelrank.app.ui.Muted
import com.novelrank.app.ui.Outline

@Composable
fun SourceSelector(
    sources: List<Source>,
    selectedId: String?,
    vertical: Boolean,
    onSelect: (String) -> Unit
) {
    if (vertical) {
        Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Text(
                "浏览网站", color = Muted, style = MaterialTheme.typography.labelLarge,
                modifier = Modifier.padding(start = 4.dp, bottom = 6.dp)
            )
            sources.forEach { source ->
                SourceItem(
                    source,
                    source.id == selectedId,
                    onSelect,
                    Modifier.fillMaxWidth()
                )
            }
        }
    } else {
        LazyRow(
            horizontalArrangement = Arrangement.spacedBy(10.dp),
            modifier = Modifier.testTag("source-list")
        ) {
            items(sources, key = { it.id }) { source ->
                SourceItem(
                    source,
                    source.id == selectedId,
                    onSelect,
                    Modifier.width(152.dp)
                )
            }
        }
    }
}

@Composable
private fun SourceItem(
    source: Source,
    isSelected: Boolean,
    onSelect: (String) -> Unit,
    modifier: Modifier
) {
    Surface(
        onClick = { onSelect(source.id) },
        modifier = modifier.testTag("source-${source.id}").semantics { selected = isSelected },
        shape = RoundedCornerShape(16.dp),
        border = BorderStroke(1.dp, if (isSelected) Ink.copy(alpha = 0.35f) else Outline),
        color = if (isSelected) MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surface
    ) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(5.dp)) {
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(if (isSelected) "●" else "○", color = Ink)
                Text(
                    source.name,
                    color = Ink,
                    fontWeight = FontWeight.SemiBold,
                    style = MaterialTheme.typography.titleSmall
                )
            }
            Text(
                "${source.categories.size} 个分类",
                color = Muted,
                style = MaterialTheme.typography.labelMedium
            )
        }
    }
}
