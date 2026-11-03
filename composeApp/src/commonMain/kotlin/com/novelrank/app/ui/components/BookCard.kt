package com.novelrank.app.ui.components

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.novelrank.app.model.Book
import com.novelrank.app.ui.Ink
import com.novelrank.app.ui.Muted
import com.novelrank.app.ui.Outline
import com.novelrank.app.ui.Warm

@Composable
fun BookCard(book: Book, compact: Boolean, onOpen: (String) -> Unit) {
    val title = book.title?.takeIf { it.isNotBlank() } ?: "书名暂未取得"
    val author = book.author?.takeIf { it.isNotBlank() } ?: "作者暂未取得"
    Surface(
        onClick = { onOpen(book.url) },
        modifier = Modifier.fillMaxWidth().testTag("book-${book.id}"),
        shape = RoundedCornerShape(18.dp),
        border = BorderStroke(1.dp, Outline)
    ) {
        Row(
            Modifier.padding(if (compact) 16.dp else 20.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(if (compact) 14.dp else 20.dp)
        ) {
            Box(
                Modifier.size(if (compact) 48.dp else 56.dp, 68.dp)
                    .background(
                        if (book.rank <= 3) Ink else MaterialTheme.colorScheme.surfaceVariant,
                        RoundedCornerShape(10.dp)
                    ),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    book.rank.toString().padStart(2, '0'),
                    color = if (book.rank <= 3) MaterialTheme.colorScheme.onPrimary else Muted,
                    fontSize = 25.sp,
                    fontWeight = FontWeight.SemiBold
                )
            }
            Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text(
                    title,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold,
                    maxLines = 2,
                    overflow = TextOverflow.Ellipsis
                )
                Text(author + (book.genre?.let { "  /  $it" } ?: ""),
                    color = Muted,
                    style = MaterialTheme.typography.bodySmall,
                    maxLines = 2,
                    overflow = TextOverflow.Ellipsis)
                if (book.metadataStatus == "partial") Text(
                    "部分作品信息未取得",
                    color = Warm,
                    style = MaterialTheme.typography.labelSmall
                )
                if (compact) Text(
                    book.metric ?: "数值未公开 / 未取得",
                    color = Ink,
                    style = MaterialTheme.typography.labelMedium
                )
            }
            if (!compact) {
                Column(
                    Modifier.width(160.dp),
                    horizontalAlignment = Alignment.End,
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Text(
                        book.metric ?: "数值未公开 / 未取得",
                        color = Ink,
                        fontWeight = FontWeight.Medium,
                        style = MaterialTheme.typography.bodyMedium
                    )
                    Text("查看原站 ↗", color = Muted, style = MaterialTheme.typography.labelSmall)
                }
            } else Text("↗", color = Muted, fontSize = 20.sp)
        }
    }
}
