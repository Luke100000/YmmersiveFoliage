package net.conczin;

import com.hypixel.hytale.server.core.plugin.JavaPlugin;
import com.hypixel.hytale.server.core.plugin.JavaPluginInit;

import javax.annotation.Nonnull;


public class YmmersiveFoliage extends JavaPlugin {
    private static YmmersiveFoliage instance;

    public YmmersiveFoliage(@Nonnull JavaPluginInit init) {
        super(init);
        instance = this;
    }

    public static YmmersiveFoliage getInstance() {
        return instance;
    }
}