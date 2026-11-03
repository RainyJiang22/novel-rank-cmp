package com.novelrank.app.data

import com.novelrank.app.model.Catalog
import com.novelrank.app.model.RankingSnapshot
import com.novelrank.app.model.Selection

interface RankRepository {
    suspend fun catalog(baseUrl: String): Catalog
    suspend fun ranking(baseUrl: String, selection: Selection, refresh: Boolean): RankingSnapshot
    fun close()
}

class ServiceException(message: String) : Exception(message)
