#include "logging_controller.h"
#include <stdio.h>
#include <argos3/core/simulator/entity/entity.h>
#include <argos3/plugins/robots/kheperaiv/simulator/kheperaiv_entity.h>
#include <string>

LOGGING_CONTROLLER::LOGGING_CONTROLLER(): _step_count(0) { }

void LOGGING_CONTROLLER::PostStep() {
    if (this->_step_count > 300) {
        fclose(this->_output_file);
        exit(1);
    }
    else {
        this->_step_count++;
        auto ents = this->GetSpace().GetEntityVector();
        for (auto ent : ents) {
            if (auto kep = dynamic_cast<CKheperaIVEntity*>(ent)) {
                auto v0 = kep->GetWheeledEntity().GetWheelVelocity(0);
                auto v1 = kep->GetWheeledEntity().GetWheelVelocity(1);
                auto pX = kep->GetEmbodiedEntity().GetOriginAnchor().Position.GetX();
                auto pY = kep->GetEmbodiedEntity().GetOriginAnchor().Position.GetY();
                fprintf(this->_output_file, "%d,%s,%f,%f,%f,%f\n", this->_step_count, &(kep->GetId().c_str())[3], v0, v1, pX, pY);
            }
            
        }
    }
}

void LOGGING_CONTROLLER::Init(TConfigurationNode& t_tree) {
    this->_output_file = fopen("test.csv", "w");
    fprintf(_output_file, "iteration,id,vl,vr,px,py\n");
}

REGISTER_LOOP_FUNCTIONS(LOGGING_CONTROLLER, "logging_controller");

