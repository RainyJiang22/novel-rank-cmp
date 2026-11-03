package com.novelrank.app.data

import io.ktor.client.HttpClient
import io.ktor.client.engine.cio.CIO

actual fun createPlatformHttpClient(): HttpClient = rankHttpClient(CIO.create())
