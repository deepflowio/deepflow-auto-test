package com.saicmobility.common.monkeyservice;

import com.saicmobility.common.envconfig.EnvConfig;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class MainApplication {

    public static void main(String[] args) {
        EnvConfig.initEnv();
        SpringApplication.run(MainApplication.class, args);
    }

}
