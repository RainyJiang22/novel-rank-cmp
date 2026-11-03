package com.novelrank.app.data

import io.ktor.client.HttpClient
import io.ktor.client.engine.darwin.Darwin

actual fun createPlatformHttpClient(): HttpClient = rankHttpClient(Darwin.create())
