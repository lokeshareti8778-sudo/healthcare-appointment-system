package com.carepoint;

import com.google.gson.Gson;
import com.google.gson.JsonParseException;
import com.microsoft.azure.functions.ExecutionContext;
import com.microsoft.azure.functions.HttpMethod;
import com.microsoft.azure.functions.HttpRequestMessage;
import com.microsoft.azure.functions.HttpResponseMessage;
import com.microsoft.azure.functions.HttpStatus;
import com.microsoft.azure.functions.annotation.AuthorizationLevel;
import com.microsoft.azure.functions.annotation.FunctionName;
import com.microsoft.azure.functions.annotation.HttpTrigger;
import java.util.Optional;
import java.util.logging.Logger;

public class AppointmentNotificationFunction {
    private static final Gson GSON = new Gson();

    @FunctionName("appointment-notification")
    public HttpResponseMessage run(
            @HttpTrigger(
                    name = "request",
                    methods = {HttpMethod.POST},
                    authLevel = AuthorizationLevel.FUNCTION)
            HttpRequestMessage<Optional<String>> request,
            final ExecutionContext context) {
        Logger logger = context.getLogger();
        String body = request.getBody().orElse("");

        try {
            AppointmentNotification notification = GSON.fromJson(body, AppointmentNotification.class);
            if (notification == null || !notification.isValid()) {
                return request.createResponseBuilder(HttpStatus.BAD_REQUEST)
                        .body("patientName, doctorName, appointmentDate, appointmentTime, and fee are required")
                        .header("Content-Type", "text/plain")
                        .build();
            }

            logger.info(String.format(
                    "Processed appointment notification for patient '%s' with doctor '%s' on %s at %s; fee=%d",
                    notification.patientName,
                    notification.doctorName,
                    notification.appointmentDate,
                    notification.appointmentTime,
                    notification.fee));

            return request.createResponseBuilder(HttpStatus.OK)
                    .header("Content-Type", "application/json")
                    .body("{\"status\":\"success\",\"message\":\"Appointment notification processed successfully\"}")
                    .build();
        } catch (JsonParseException | NumberFormatException exception) {
            logger.warning("Invalid appointment notification payload: " + exception.getMessage());
            return request.createResponseBuilder(HttpStatus.BAD_REQUEST)
                    .body("Invalid JSON payload")
                    .header("Content-Type", "text/plain")
                    .build();
        }
    }

    private static final class AppointmentNotification {
        private String patientName;
        private String doctorName;
        private String appointmentDate;
        private String appointmentTime;
        private Integer fee;

        private boolean isValid() {
            return hasText(patientName)
                    && hasText(doctorName)
                    && hasText(appointmentDate)
                    && hasText(appointmentTime)
                    && fee != null
                    && fee >= 0;
        }

        private static boolean hasText(String value) {
            return value != null && !value.trim().isEmpty();
        }
    }
}
