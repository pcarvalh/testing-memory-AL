# Apprentice Learner - Memory Overview

## Downloading and Use

The current implementation of the memory mechanism is available [here](https://github.com/apprenticelearner/AL_Core/tree/testing-we). In order to use the memory mechanism, modify your JSON file to include the agent-level argument `use_memory: True` (see `generate_json.py`, and then run AL as normal. Currently, the agent relies on specific features in the BRD, in order to account for initial activation level based on question type.

## Description of Memory Mechanism

The memory mechanism is based on the [ACT-R](https://www.semanticscholar.org/paper/Using-a-model-to-compute-the-optimal-schedule-of-Pavlik-Anderson/80bebc6e48ab0b7c3cb420839ecbd516ecb5b790) modeling system. In particular, the memory mechanism in AL replicates the activation and decay models described in the Pavlik & Anderson paper. The activation for a given skill at time $n$ is determined by the equation:
$$
m_n = \beta_i + \ln \left( \sum_{k=1}^n t_k^{-d_k}\right)
$$
where $t_k$ is the age of the $k^{th}$ trial, $d_k$ is the decay for the $k^{th}$ trial, and $\beta_i$ represents differences in activation increase between different types of questions.

Decay for a a given skill at time $k$ is given by the equation:
$$
d_k = ce^{m_{k-1}} + \alpha
$$
where $c$ is a decay scale parameter, $m_{k-1}$ is the activation level of the previous trial, and $\alpha$ is the intercept of the decay function.

The probability that a skill will be recalled during testing is dependent on its activation:
$$
p(m) = \dfrac{1}{1+e^{\frac{\tau-m}{s}}}
$$
where $\tau$ is a threshold parameter, and $s$ controls the sensitivity of recall to changes in activation.

## Implementation

Because the decay function used in this model is recursive and depends on previous activations, the activations for every skill are stored upon every time step (time increases whenever AL takes an action). Activation for a specific skill increases whenever AL uses it on a problem, or requests a bottom-out hint. The activation increase depends on a constant coefficient, $\beta_i$. Currently, $\beta_i = 0$ for retrieval practice questions, and $\beta_i = 4$ for worked examples, as we hypothesize that completing worked examples causes higher initial activation than retrieval practice, but causes faster decay due to the recursive nature of the model. The decay scale parameter is the same for both types of questions, $c=0.277$. The activations for the other skills that AL has learned is then recalculated, according to the decay function (in this experiment, $\alpha$ = 0.177).

When the agent requests an answer/action from AL, the where/when learners return a list of applicable skills for the problem state. The probability of AL recalling the first skill in the list is calculated according to the equation above, with $\tau=-0.7, s=1$. If  the skill is retrieved, AL performs the action (and possibly receives feedback depending on the question type, triggering activation recalculation). If the skill is not retrieved, AL attempts to retrieve each subsequent skill in the list. If no skills are retrieved, AL requests a bottom-out hint from the tutor.

## Code Locations

The activation and decay models is implemented within the `train` function in the `ModularAgent`. The `activations` dictionary keeps track of sequential activations for each skill, and the `exp_inds` dictionary keeps track of the times at which each skill is activated. Upon first activation of a skill, it is added to `activations`, and initialized with an activation of `-Inf`. This is needed, as decay depends on the previous activation (with $m_0 = $ `-Inf`, $d_1 = \alpha$ ). Whenever a skill is activated, the current time is logged in the `exp_inds` dictionary. Afterwards, activation (including decay) is recalculated for all skills using the recursive model, with age for each skill given by `self.t - self.exp_inds[str_exp]` (note that this produces an array for each skill), and time is incremented.

The $\beta_i$ coefficient is determined by examining a specific element in the state, and changing it based on the value: `state["?ele-practice_type"]["value"]`. This is specific to this project.

Retrieval is calculated in the `request` function. 



