# Portal Android ProGuard Rules
-keepattributes Signature
-keepattributes *Annotation*
-keep class com.portal.data.model.** { *; }
-keep class com.portal.data.api.** { *; }
-keep class com.portal.data.repository.** { *; }
-keep class com.portal.ui.** { *; }
-keep class com.portal.PortalApp { *; }

# Gson
-keepattributes Signature
-keepattributes *Annotation*
-dontwarn sun.misc.**
-keep class com.google.gson.** { *; }
-keep class * implements com.google.gson.TypeAdapterFactory
-keep class * implements com.google.gson.JsonSerializer
-keep class * implements com.google.gson.JsonDeserializer

# OkHttp
-dontwarn okhttp3.**
-dontwarn okio.**
-dontwarn javax.annotation.**

# Glide
-keep public class * implements com.bumptech.glide.module.GlideModule
-keep class com.bumptech.glide.** { *; }

# Kotlin
-keep class kotlin.** { *; }
-keep class kotlinx.** { *; }
-dontwarn kotlin.**
