package com.novelrank.app.ui.components

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.novelrank.app.presentation.RankUiState
import com.novelrank.app.ui.Ink
import com.novelrank.app.ui.Muted
import com.novelrank.app.ui.Outline

@Composable
fun RankingFilters(state: RankUiState, onCategory: (String) -> Unit, onBoard: (String) -> Unit, onSearch: (String) -> Unit) {
    val source = state.source ?: return
    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            FilterPicker("分类", "category", state.category?.let { "${it.group} · ${it.name}" }.orEmpty(),
                source.categories.map { it.id to "${it.group} · ${it.name}" }, onCategory, Modifier.weight(1f))
            FilterPicker("榜单", "board", state.board?.name.orEmpty(),
                source.boards.filter { it.id in state.category?.boardIds.orEmpty() }.map { it.id to it.name }, onBoard, Modifier.weight(1f))
        }
        OutlinedTextField(value = state.query, onValueChange = onSearch,
            modifier = Modifier.fillMaxWidth().testTag("ranking-search"), singleLine = true, shape = RoundedCornerShape(14.dp),
            placeholder = { Text("搜索前十中的书名或作者", style = MaterialTheme.typography.bodyMedium) },
            trailingIcon = {
                if (state.query.isNotEmpty()) TextButton(onClick = { onSearch("") }, modifier = Modifier.testTag("clear-search")) { Text("清除") }
            })
    }
}

@Composable
private fun FilterPicker(label: String, tag: String, selection: String, options: List<Pair<String, String>>,
                         onSelect: (String) -> Unit, modifier: Modifier) {
    var expanded by remember { mutableStateOf(false) }
    Box(modifier) {
        Surface(onClick = { expanded = true }, shape = RoundedCornerShape(14.dp),
            border = BorderStroke(1.dp, Outline), modifier = Modifier.fillMaxWidth().testTag("picker-$tag")) {
            Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(5.dp)) {
                Text("$label  ▾", color = Muted, style = MaterialTheme.typography.labelMedium)
                Text(selection, color = Ink, fontWeight = FontWeight.Medium, style = MaterialTheme.typography.bodyMedium,
                    maxLines = 2, overflow = TextOverflow.Ellipsis)
            }
        }
        DropdownMenu(expanded = expanded, onDismissRequest = { expanded = false }, modifier = Modifier.heightIn(max = 360.dp)) {
            options.forEach { (id, name) ->
                DropdownMenuItem(text = { Text(name) }, modifier = Modifier.testTag("option-$tag-$id"),
                    onClick = { expanded = false; onSelect(id) })
            }
        }
    }
}
