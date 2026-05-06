/**
 * UI Controller for Joy Luck Club Understanding Engine
 */

document.addEventListener('DOMContentLoaded', () => {
    const analyzeBtn = document.getElementById('analyze-btn');
    const resetBtn = document.getElementById('reset-btn');
    const userInput = document.getElementById('user-input');
    const inputZone = document.getElementById('input-zone');
    const resultsZone = document.getElementById('engine-results');
    const stepCards = document.querySelectorAll('.step-card');
    const suggestBtn = document.getElementById('suggest-btn');
    const suggestionModal = document.getElementById('suggestion-modal');
    const closeModal = document.querySelector('.close-modal');
    const suggestionBody = document.getElementById('suggestion-body');

    analyzeBtn.addEventListener('click', () => {
        const text = userInput.value.trim();
        if (!text) {
            alert('Please enter some text to analyze.');
            return;
        }

        performAnalysis(text);
    });

    resetBtn.addEventListener('click', () => {
        resultsZone.classList.add('hidden');
        inputZone.classList.remove('hidden');
        userInput.value = '';
        
        // Reset animations
        stepCards.forEach(card => card.classList.remove('active'));
    });

    suggestBtn.addEventListener('click', () => {
        const text = userInput.value;
        const results = window.DifferenceEngine.analyze(text);
        generateSuggestions(results);
        suggestionModal.classList.remove('hidden');
    });

    closeModal.addEventListener('click', () => {
        suggestionModal.classList.add('hidden');
    });

    window.addEventListener('click', (e) => {
        if (e.target === suggestionModal) {
            suggestionModal.classList.add('hidden');
        }
    });

    function generateSuggestions(results) {
        const suggestions = [
            {
                title: "Practice 'Narrative Sharing'",
                desc: `Regarding the "${results.values}" conflict, avoid direct debate. Try asking: "Mother/Daughter, what was your greatest fear at my age?" Shared history builds empathy.`
            },
            {
                title: "Translate the Hidden Heart",
                desc: `Decode words that sound like criticism. If they say "You don't listen," the actual intent is often "I'm worried about your safety." Respond with understanding of their protective instinct.`
            }
        ];

        suggestionBody.innerHTML = suggestions.map(s => `
            <div class="suggestion-item">
                <h4>${s.title}</h4>
                <p>${s.desc}</p>
            </div>
        `).join('');

        // Populate Dialogue Scripts
        const parentsBubble = document.querySelector('#dialogue-parent .bubble');
        const childrenBubble = document.querySelector('#dialogue-child .bubble');
        const parentsIntent = document.querySelector('#dialogue-parent .intent-label');
        const childrenIntent = document.querySelector('#dialogue-child .intent-label');

        if (results.values.includes("Individualism")) {
            parentsIntent.innerHTML = "Intent: Expression of Fear & Creating a Safe Haven";
            parentsBubble.innerHTML = "<em>(Surface: You are disobedient, you'll regret this)</em><br><strong>Translated:</strong> 'I'm not trying to control you. I'm just afraid you're moving too fast and will forget how to protect yourself. If you fail out there, I want this home to be your only safe harbor.'";
            
            childrenIntent.innerHTML = "Intent: Seeking Support for Independence & Cultural Acceptance";
            childrenBubble.innerHTML = "<em>(Surface: Leave me alone)</em><br><strong>Translated:</strong> 'Mother, I know your strictness comes from protection. I chose this path to fulfill the 'possibility of freedom' you gave me. Please believe that the resilience you taught me is enough.'";
        } else if (results.values.includes("Success")) {
            parentsIntent.innerHTML = "Intent: Intergenerational Projection & Social Mobility";
            parentsBubble.innerHTML = "<em>(Surface: You should be as good as Waverly)</em><br><strong>Translated:</strong> 'You are my hope. I push you because I'm afraid you won't have a shield in this cruel world. I want you to have the power and voice that I never had.'";
            
            childrenIntent.innerHTML = "Intent: Separating Worth from External Metrics";
            childrenBubble.innerHTML = "<em>(Surface: I hate the piano)</em><br><strong>Translated:</strong> 'I used to think I was just a trophy for you, but I see now that you were teaching me how to fight. I will succeed my own way, not just through that piano.'";
        } else {
            parentsIntent.innerHTML = "Intent: Implicit Love & Intergenerational Healing";
            parentsBubble.innerHTML = "<em>(Surface: Silence or Criticism)</em><br><strong>Translated:</strong> 'Please forgive me for losing the ability to express tenderness. Every harsh word I say has 'be careful, I want you to win' behind it. My silence is also to protect you from the pain of my past.'";
            
            childrenIntent.innerHTML = "Intent: Breaking the Cycle of Silence & Connection";
            childrenBubble.innerHTML = "<em>(Surface: We have nothing to talk about)</em><br><strong>Translated:</strong> 'I am no longer trying to gain freedom through confrontation. I want to hear your stories—the real lives behind the 'broken English'. Let's try a new way of understanding each other.'";
        }
    }

    function performAnalysis(text) {
        // Hide input, show results
        inputZone.classList.add('hidden');
        resultsZone.classList.remove('hidden');

        // Run the engine
        const results = window.DifferenceEngine.analyze(text);

        // Update DOM
        document.getElementById('result-values').textContent = results.values;
        document.getElementById('result-context').textContent = results.context;
        document.getElementById('result-trauma').textContent = results.trauma;
        document.getElementById('result-identity').textContent = results.identity;
        document.getElementById('result-narrative').textContent = results.methodology_narrative;
        document.getElementById('result-translation').textContent = results.methodology_translation;
        document.getElementById('result-final').textContent = results.final;

        // Animate cards sequentially
        stepCards.forEach((card, index) => {
            setTimeout(() => {
                card.classList.add('active');
            }, (index + 1) * 300);
        });
    }

    // Export functionality (mockup)
    document.getElementById('export-btn').addEventListener('click', () => {
        alert('Analysis report exported (Simulated). In a production app, this would generate a PDF or email.');
    });
});
