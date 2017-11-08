
const questions = {};

export default class Question{

    constructor(question){
        if(questions.hasOwnProperty(question.id.toString())){
            return questions[question.id];
        } else {
            this.id = question.id;
            this.question = question.question;
            this.help_text = question.help_text;
            this.question_type = question.question_type;
            this.required = question.required;
        }
    }

}
