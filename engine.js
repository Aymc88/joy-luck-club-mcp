/**
 * Joy Luck Club Difference Understanding Engine - Core Logic
 */

const EngineDimensions = {
    LAYER_1: {
        title: "Conflict Identification",
        clashes: [
            { id: 'values', label: "Value Clash", options: ["Filial Piety vs. Individualism", "Collective Honor vs. Personal Happiness", "Obedience vs. Independence"] },
            { id: 'context', label: "Context Misalignment", options: ["High-Context Implied vs. Low-Context Direct", "Between the Lines vs. Literal Meaning"] },
            { id: 'projection', label: "Expectation Protection", options: ["Perfectionist Overcompensation", "Survival-based Achievement", "Trophy vs. Self-Worth"] }
        ]
    },
    LAYER_2: {
        title: "Behavioral Analysis",
        mechanisms: [
            { id: 'silence', label: "Mechanism of Silence", options: ["Intergenerational Trauma", "Protective Reticence", "Structural Lack of Communication"] },
            { id: 'assimilation', label: "Assimilation Crisis", options: ["Roots as a Price for Freedom", "The Cost of Pseudo-Assimilation", "Escaping Cultural Labels"] }
        ]
    },
    LAYER_3: {
        title: "Methodology Engine",
        solutions: [
            { id: 'narrative', label: "Narrating Trauma", options: ["Uncovering Scars for Empowerment", "Healing through Shared Pain", "Reconstructing Resilience"] },
            { id: 'translation', label: "Love Translation", options: ["Reading 'Life's Importance'", "Deep Love behind Broken English", "Motivation vs. Confrontation"] }
        ]
    },
    LAYER_4: {
        title: "Ultimate Synthesis",
        outcome: "Achieving Unification (Integration) and Embracing Dual Identity."
    }
};

const Keywords = {
    independent: ['independent', 'freedom', 'choice', 'career', 'job', 'future', '独立', '自由', '选择'],
    filial: ['parents', 'obey', 'filial', 'family', 'honor', '父母', '听话', '孝顺', '家族', '丢脸'],
    silence: ['silent', 'quiet', 'hide', 'secret', 'no talk', '不想说', '沉默', '秘密', '不理解', '没沟通'],
    success: ['piano', 'chess', 'competition', 'win', 'success', '钢琴', '棋', '比赛', '名牌', '成功'],
    trauma: ['history', 'pain', 'war', 'past', 'grandma', '过去', '战争', '痛苦', '奶奶', '姥姥']
};

class DifferenceEngine {
    constructor() {}

    analyze(text) {
        const lowerText = text.toLowerCase();
        let results = {
            values: "Filial Piety vs. Individualism",
            context: "High-context (Implied) vs. Low-context (Direct)",
            trauma: "Generational Trauma Inheritance",
            identity: "Search for Cultural Belonging",
            methodology_narrative: "Empowerment through Narrating Trauma",
            methodology_translation: "Re-translating Implicit Acts of Love",
            final: "“The Chinese part of me... it's my family.”"
        };

        // Keyword detection
        if (this.hasAny(lowerText, Keywords.independent)) {
            results.values = "Individual Autonomy vs. Filial Expectations";
        }
        
        if (this.hasAny(lowerText, Keywords.success)) {
            results.identity = "Deconstructing the 'Prodigy' Narrative";
        }

        if (this.hasAny(lowerText, Keywords.trauma)) {
            results.trauma = "Survival Trauma turned into Modern Pressure";
            results.methodology_narrative = "Breaking Barriers through Shared History";
        }

        return results;
    }

    hasAny(text, list) {
        return list.some(k => text.includes(k));
    }
}

window.DifferenceEngine = new DifferenceEngine();
