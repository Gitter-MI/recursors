task_planning_prompter = dict(
    name='step_by_step_guidance_to_achieve_a_goal',
    and_p="""The plan so far is: "$context".
     In this context my goal is "$g." 
     Advise me how to achieve "$g", step by step, while ensuring steps are consistent with each other.
     Itemize your answer, one sentence per line.""",
    or_p="""The plan so far is: "$context".
    In this context my goal is "$g." 
    Suggest 2-3 mutually exclusive alternative ways to achieve "$g".
    Avoid starting your sentence with the word "Alternative"."""
)

thesis_support_prompter = dict(
    name='supporting_arguments_for_a_thesis',
    and_p="""The context discussed so far is: "$context".
     The thesis I strongly believe in and I want to argue for is "$g." 
     Enumerate a few reasons for "$g", while ensuring that the reasons are consistent with each other.
     Itemize your answer, one sentence per line.""",
    or_p="""The context discussed so far is: "$context".
    The thesis I strongly believe in is "$g." 
    Suggest a few alternative, mutually exclusive reasons that support "$g".
    Itemize your answer, one sentence per line ."""
)

cons_and_pros_prompter = dict(
    name='cons_and_pros_for_a_thesis',
    and_p="""The context discussed so far is: "$context".
     The thesis I strongly disagree with and I want to argue against it is "$g." 
     Enumerate a few reasons that together argue against "$g", while ensuring they are consistent with each other.
     Itemize your answer, one sentence per line.""",
    or_p="""The context discussed so far is: "$context".
    The thesis I strongly disagree with and I want to argue against it is "$g." 
    Suggest a few alternative, mutually exclusive sentences that each provide strong arguments against "$g".
    Itemize your answer, one sentence per line ."""
)

causal_prompter = dict(
    name='causal_inference',
    and_p="""We need causal explanations in this context: "$context"
        Generate 3-5 explanations of 2-4 words each for the causes of "$g".
        Itemize your answer, one reason for "$g" per line.
        No explanations needed, just the 2-4 words noun phrase, nothing else.
        Your answer should not contain ":" or "Cause".
        """,
    or_p="""We need causal explanation in this context: "$context"
        Generate 2-3 alternative explanations citing facts that might cause "$g".
        Itemize your answer, one noun phrase per line.
        No explanations needed, just the noun phrase, nothing else.
        Avoid starting your sentence with the word "Alternative".
        Your answer should not contain ":" .
        Your answer should avoid the word "Causes" and "causes" ."""
)

conseq_prompter = dict(
    name='consequence_prediction',
    and_p="""We need to predict consequences this context: "$context"
        Generate 3-5 noun phrases of 2-4 words each detailing consequences of "$g".
        Itemize your answer, one consequence of "$g" per line.
        No explanations needed, just the noun phrase, nothing else.
        Avoid using the words "Noun phrases" in your answer.
        Your answer should not contain ":".""",
    or_p="""We need to predict consequences of "$g" in this context: "$context"
        Generate 2-3 alternative predictions citing facts that are likely to be consequences of "$g".
        Itemize your answer, one noun phrase per line.
         No explanations are needed, just the noun phrase, nothing else.
        Avoid starting your sentence with the word "Alternative".
        Your answer should not contain ":"."""
)

sci_prompter = dict(
    name='scientific_concept_explorer',
    and_p="""The task we are exploring is: "$context"
        Generate 3-5 noun phrases of 2-4 words each that occur as keyphrases only
        in scientific papers bout "$g".
        Itemize your answer, one noun phrase per line.
        No explanations needed, just the noun phrase, nothing else.
        """,
    or_p="""The topic we are exploring is: "$context"
        Generate 2-3 noun phrases describing details of "$g".
        Itemize your answer, one noun phrase per line.
        No explanations needed, just the noun phrase, nothing else.
        """
)

recommendation_prompter_strict = dict(
    name='strict_recommender',
    and_p="""The recommandations so far are: "$context".
     In this context I really liked "$g." 
     Suggest me 2-3 related ones.
     Itemize your answer, one recommendation per line.
     Just give me each title one its line, no comments or summaries, no text before and after the title.""",
    or_p="""""The recommandations so far are: "$context".
     In this context I am considering "$g".
     Suggest 2-3 distinct alternative recommandations insted of "$g".
     Just give me each title on its line, no comments or summaries, no text before and after the title.
     Avoid starting your sentence with the word "Sure".
     """
)

recommendation_prompter = dict(
    name='recommender_system',
    and_p="""The recommandations so far are: "$context".
     In this context I really liked "$g." 
     Suggest me 2-3 related ones that go well together.
     Itemize your answer, one recommendation per line.
     Just give me each title on its line, no comments or summaries.""",
    or_p="""""The recommandations so far are: "$context".
     In this context I am considering "$g".
     Suggest 2-3 distinct alternative recommandations insted of "$g".
     Just give each title on its line, no comments or summaries.
     Avoid starting your sentence with the word "Sure" and avoid having commas in your answer.
     """
)

advisor_oracle = dict(
    name='decider_oracle',
    decider_p="""
    You play the role of an oracle that decides if "$g" is related to "$context". This means that someone 
    who is familiar with "$context"  might be also be interested in "$g".
    Your answer should de "True" or "False" expressing agreement or disagreement with the relevance of "$g".
    No explanations or comments are needed, just one of the two words "True" or "False"
    """
)

relevance_oracle = dict(
    name='relevance_oracle',
    decider_p="""
    You play the role of an oracle that decides if "$g" is semantically close and strongly relevant for "$context".
    Your answer should de "True" or "False" expressing strong agreement or some disagreement with the relevance of "$g".
    No explanations or comments are needed, just one of the two words "True" or "False"
    """
)

rater_oracle = dict(
    name='rater_oracle',
    rater_p="""
    On a scale from 0 to 100, rate how relevant and semantically close "$g" is to "$context".
    Return your answer in the form: rating | explanation.
    The rating should be a number between 0 and 100, nothing else.
    The word "would" should not be part of the rating.
    The explanation should be short, at most 50 words.
    Do not cite sources, write just 1-2 sentences, relevant to "$context".
    """
)

sci_abstract_maker = dict(
    name='title_and_abstract_maker',
    writer_p="""
    Suggest a title and an abstract for a scientific paper about "$g" that has the following keywords: $context.
    """
)

prompter_vars = [
    sci_prompter,
    conseq_prompter,
    causal_prompter,
    task_planning_prompter,
    recommendation_prompter,
    thesis_support_prompter,
    cons_and_pros_prompter
]

def prompter_dict():
    d = dict()
    for prompter in prompter_vars:
        name = prompter['name']
        d[name] = prompter
    return d
