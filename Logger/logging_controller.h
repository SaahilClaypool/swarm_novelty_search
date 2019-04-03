#ifndef LOGGING_CONTROLLER_H
#define LOGGING_CONTROLLER_H
 
/*
 * Include some necessary headers.
 */
#include <argos3/core/simulator/loop_functions.h>
#include <stdio.h>

/*
 * All the ARGoS stuff in the 'argos' namespace.
 * With this statement, you save typing argos:: every time.
 */
using namespace argos;
 
/*
 * A controller is simply an implementation of the CCI_Controller class.
 */
class LOGGING_CONTROLLER : public CLoopFunctions {
 
public:
 
   /* Class constructor. */
   LOGGING_CONTROLLER();

   virtual void Init(TConfigurationNode& t_tree); 
 
   /* Class destructor. */
   virtual ~LOGGING_CONTROLLER() {}
 
   /*
    * This function is called once every time step.
    * The length of the time step is set in the XML file.
    */
   virtual void PostStep();
 
   /*
    * This function resets the controller to its state right after the
    * Init().
    * It is called when you press the reset button in the GUI.
    * In this example controller there is no need for resetting anything,
    * so the function could have been omitted. It's here just for
    * completeness.
    */
   virtual void Reset() {}
 
   /*
    * Called to cleanup what done by Init() when the experiment finishes.
    * In this example controller there is no need for clean anything up,
    * so the function could have been omitted. It's here just for
    * completeness.
    */
   virtual void Destroy() {}
 
private:
   int _step_count;
   FILE* _output_file;
 
 
};
 
#endif