package com.example.aigrader;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@SpringBootApplication
public class AiGraderApplication {

    public static void main(String[] args) {
        SpringApplication.run(AiGraderApplication.class, args);
    }

}

// This class will handle incoming web requests
@RestController
class GreetingController {

    // This annotation enables Cross-Origin Resource Sharing (CORS),
    // allowing your HTML frontend to communicate with this backend.
    @CrossOrigin(origins = "*") 
    @GetMapping("/") // This maps the root URL ("/") to this method
    public String index() {
        return "AI Grader Java backend is running!";
    }
}
