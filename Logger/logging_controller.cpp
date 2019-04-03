#include "logging_controller.h"
#include <stdio.h>

LOGGING_CONTROLLER::LOGGING_CONTROLLER(): _step_count(0) { }

void LOGGING_CONTROLLER::PostStep() {
    if (this->_step_count > 300) {
        fclose(this->_output_file);
        exit(1);
    }
    else {
        this->_step_count++;
        fprintf(this->_output_file, "%d\n", this->_step_count);
    }
}

void LOGGING_CONTROLLER::Init(TConfigurationNode& t_tree) {
    this->_output_file = fopen("test.csv", "w");
}

REGISTER_LOOP_FUNCTIONS(LOGGING_CONTROLLER, "logging_controller");

