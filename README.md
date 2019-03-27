# swarm_novelty_search
CS 525 Swarm Intelligence novelty search behavior discovery 


# General idea

search.py will handle the novelty search and orchestrate the algorithms. 
It will: 
1. Create the populations (defined by the neural network weights only)
2. Create an Argos / Buzz program with those weights

    Because I don't want to learn Buzz too well, I would recommend just templating the buzz files like this: 

    **buzz file**
    ```
    var w0 = {WEIGHT_0}
    var w1 = {WEIGHT_1}
    var w2 = {WEIGHT_2}
    ```

    **search.py**
    ```py
    buzz_file = f.open().read().replace("{WEIGHT_0}", w0).replace("{WEIGHT_1}", w1)...
    ```

    Note: orignally, I thought we could write these to subdirectories. 
    But, I think keeping the parameters in memory and immediatly deleting files after each run will be cleaner - otherwise we will create thousands of directories which are hard to look through.

3. Start a process to run Argos / Buzz

    Buzz should periodically write out the measurements to a csv over the simulation.
    We should be able to run Argos in a headless manner (hopefully) so this is faster / doable on a remote server without a connected display. 

4. Measure the novelty of the features (output csv)
5. Store and permute the novel populations


