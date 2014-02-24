#	mengl
mengl is a mixset of the C and Pascal language.

##	The Lex Grammer

###	keywords:
	array 				ARRAY 
	break				BREAK
	continue			CONTINUE
	do					DO
	else 				ELSE
	function 			FUNCTION
	if 					IF
	int 				INT
	of 					OF
	pointer to 			POINTER TO
	return 				RETURN
	sizeof				SIZEOF
	struct				STRUCT
	void				VOID
	unsigned			UNSIGNED
	while				WHILE

###	operator
	>>					RS
	<<					LS
	->					PTR
	&&					AND
	||					OR
	<=					LE
	=>					GE
	==					EQ
	!=					NE
	=					'='
	.					'.'
	&					'&'
	|					'|'
	+					'+'
	-					'-'
	*					'*'
	/					'/'
	>					'>'
	<					'<'
	(					'('
	)					')'
	[					'['
	]					']'
	{					'{'
	}					'}'
	;					';'
	'					
	"					

##	The Grammer

	program						->	struct_declaration_list struct_definition_list function_declaration_list function_definition_list

	struct_declaration_list 	->	struct_declaration_list struct_declaration
								| 	ε

	struct_declaration 			->	STRUCT IDENTIFIER ';'
 
	struct_definition_list 		->	struct_definition_list struct_definition
								|	ε

	struct_definition 			->	STRUCT IDENTIFIER '{' variable_declaration_list '}' ';'

	function_declaration_list 	->	function_declaration_list function_declaration
								|	ε

	function_declaration 		->	FUNCTION IDENTIFIER '('  parameter_list ')' 
	basic_specifier';'

	parameter_list 				->	parameters 
								| 	void

	parameters 					->	parameters ',' parameter
								|	parameter

	parameter 					->	IDENTIFIER ':' type_specifier 

	function_definition_list 	->	function_definition_list function_declaration
								|	ε

	function_definition 		-> 	FUNCTION IDENTIFIER compound_statement ';'

	variable_declaration_list 	->	variable_declaration_list variable_declaration 
								|	ε

	variable_declaration 		->	IDENTIFIER ':' type_specifier ';'

	type_specifiers 			->	type_specifiers ',' type_specifier
								|	type_specifier

	type_specifier 				->	basic_specifier
								|	struct_specifier
								|	function_specifier
								|	array_specifier
								|	pointer_specifer

	basic_specifier				->	INT
								|	UNSIGNED
								|	VOID

	struct_specifier			->	STRUCT IDENTIFIER

	function_specifier 			->	FUNCTION '(' type_specifiers ')' basic_specifier

	array_specifier				->	ARRAY '[' num ']' OF type_specifier

	pointer_specifer			->	POINTER TO type_specifier

	statement_list				->	statement_list statement 
								|	ε

	statement 					->	selection_statement
								|	iteration_statement
								|	jump_statement
								|   assign_statement
								|	compound_statement
								|	expresstion_statement


	selection_statement			->	IF '(' logical_expression ')' statement
								| 	IF '(' logical_expression ')' statement ELSE statement

	iteration_statement 		->	WHILE '(' logical_expression ')' statement
								|	DO statement WHILE '(' logical_expression ')' ';'

	jump_statement 				->	CONTINUE ';'
								|	BREAK ';'
								|	RETURN ';'
								|	RETURN logical_expression ';'

	assign_statement            ->  '@' unary_expression '=' logical_expression ';'

	compound_statement			->	'{'	variable_declaration_list statement_list '}'
	
	expression_statement		->	logical_expression ';'
								|	';'

	logical_expression 			-> 	logical_expression OR logical_and_expression
								|	logical_and_expression 

	logical_and_expression		->	logical_and_expression AND inclusive_or_expression
								|	inclusive_or_expression

	inclusive_or_expression		->	inclusive_or_expression '|' exclusive_or_expression
								|	exclusive_or_expression

	exclusive_or_expression		->	exclusive_or_expression '^' and_expression
								|	and_expression

	and_expression 				->	and_expression '&' equality_expression 
								|	equality_expression

	equality_expression 		->	equality_expression EQ 	relational_expression
								|	equality_expression NE 	relational_expression
								|	relational_expression

	relational_expression 		->	relational_expression '<' shift_expression
								|	relational_expression '>' shift_expression
								| 	relational_expression LE  shift_expression
								|	relational_expression GE  shift_expression
								|	shift_expression

	shift_expression 			->	shift_expression LS additive_expression
								|	shift_expression RS additive_expression
								|	additive_expression

	additive_expression 		->	additive_expression '+' multiplicative_expression
								|	additive_expression '-' multiplicative_expression
								|	multiplicative_expression

	multiplicative_expression 	->	multiplicative_expression '*' cast_expression
								|	multiplicative_expression '/' cast_expression
								|	cast_expression

	cast_expression 			->	cast_expression CAST TO type_specifier
								|	unary_expression
						
    unary_expression 			->	unary_operator unary_expression
    							|	postfix_expression

    unary_operator 				->	'*'
    							|	'&'

    postfix_expression 			->	postfix_expression '.' IDENTIFIER
    							|	postfix_expression PTR IDENTIFIER
    							|	postfix_expression '[' logical_expression ']'
    							|   postfix_expression '(' argument_list ')'
    							|	primary_expression

    primary_expression 			->	CONSTANT
    							|	'(' logical_expression ')'
    							|	IDENTIFIER

    argument_list 				->	arguments | ε

    arguments 					->	arguments ',' logical_expression
    							|	logical_expression


##	Code Gen
	mengl constructs an ast from the input program, generates the liner three address code 
	through a tree walk and implements a simplest stack machine to translate the tacode into 
	target machine's instruct set. 

###	program demo
	a demo program that mengl take as input.

	//struct declaration
	struct process;

	//function declaration
	function register_process(p : pointer to struct process) int;
	function main(void) int;

    //global variable declaration
	pid : int;
	processes : array [10] of pointer to struct process;

	//struct definition
	struct process{
		pid : int;
		func: pointer to function (pointer to void) int;
		data: pointer to void;
	};

	//function definintion
	function register_process{
		@ pid = pid + 1;
		if (pid >= 10)
			return -1;
		@ processes[pid] = p;
		@ pid->pid = pid;
		return 0;
	};
	function main{
		i : ret;
		ret : int;
		pro : struct process;

		@ ret = register_process(&pro);
		return 0;
	};

###	IR of The Demo
	through a tree walk, we get the irs.(I extend the dragon book's front to represent the ast)
	main :
		l0: t0 = &pro
			param t0
 			call register_process, 1
 			loadret t1
 			ret = t1
		l2: saveret 0
 			goto l1
		l1: ret

	register_process :
		l0: t0 = pid + 1
			pid = t0
		l2: iffalse pid >= 10 goto l3
		l4: t1 = -1
 			saveret t1
 			goto l1
		l3: t2 = pid * 4
			processes offset t2 = p
		l5: p offset 0 = pid
		l6: saveret 0
 			goto l1
		l1: ret

###	Target instruct Set
	logic: 
		ANDR
		ANDI
		ORR
		ORI
		XORR
		XORI
	arith:
		ADDSR
		ADDSI
		ADDUR
		ADDUI
		SUBSR
		SUBSI
		MULSR
		MULSI
		MULUR
		MULUI
		DIVSR
		DIVSI
		DIVUR
		DIVUI
	shift:
		SHRLR
		SHRLI
		SHLLR
		SHLLI
	branch:
		BE
		BNE
		BSGT
		BUGT
		JMP
		CALL
	mem:
		LDW
		STW

###	Register Assignment
	gpr0 as stack pointer register(sp)
	gpr1 as frame pointer register(fp)
	gpr2 as code segment register(cs)
	gpr3 as static area register(ds)
	gpr5 as a accumulate register for storing operation's result(acc)
	gpr6 and gpr7 as the operator registers(op1, op2)


###	Runtime Structure

			before call:
						 	
										 _
							|  param0   | \ 
							|	 .		|  \
							|	 .		|  |
							|  paramn	|  |
					fp->	|	oldfp	|  |
							|	ret 	|  |
							|  local0	|  |	current frame
							|	 .		|  |
							|	 .		|  |	
							|  localm	|  |
							|  temp0	|  |
							|    .		|  |
							|    .		|  /	
							|  tempt	|_/
							|	 .		|
							|	 .		|
							|	 .		|
					sp->	|	 .		|



			after call:

							|	localm	|  |	old frame
							|	temp0	|  |
							|	 .		|  |
							|	 .		|  /
							|	tempn	|_/
							|	 .		|
							|	 .		|
							|	 .		|_
							|			| \	
							|  param0   |  \ 
							|	 .		|  |
							|	 .		|  |
							|  paramn	|  |
					fp->	|	oldfp	|  |<-push old fp
					(sp->)	|   ret 	|  |<-push ret address
							|  local0	|  |<-skip local variables
							|	 .		|  |	new frame
							|	 .		|  |	
							|  localm	|  |
							|  temp0	|  |
							|    .		|  |
							|    .		|  /	
					sp->	|  tempt	|_/
							|			|
							|			|

###	Target Code
	it translate t0 = pid + 1 (the 1st line ir code from register_process) into:
		addsi r3, r5, 48 	<-compute pid's addr (pid sits in the static area with a offset of 48 from ds)
		addsi r0, r0, 4  	<-inc sp
		stw r0, r5, 0 	 	<-push pid's addr into stack
		ldw r0, r5, 0 	 	<-pop pid's addr from stack 
		addsi r0, r0, -4 	<-dec sp
		ldw r5, r5, 0 	 	<-load pid's value
		addsi r0, r0, 4  	<-inc sp
		stw r0, r5, 0 	 	<-push pid's value into stack
		addsi r4, r5, 4  	<-compute the 1's addr (1 sit in the const area with a offset of 4 from ds)
		addsi r0, r0, 4  	<-inc sp
		stw r0, r5, 0 		<-push 1's addr into stack
		ldw r0, r5, 0 		<-pop 1's addr from stack
		addsi r0, r0, -4 	<-dec sp
		ldw r5, r5, 0 		<-load 1's value
		addsi r0, r0, 4 	<-inc sp
		stw r0, r5, 0 		<-push 1's value into stack
		ldw r0, r6, 0 		<-pop 1's value into op1
		addsi r0, r0, -4 	<-dec sp
		ldw r0, r7, 0 		<-pop pid's value into op2
		addsi r0, r0, -4 	<-dec sp
		addsr r6, r7, r5 	<-compute pid + 1 and store result into acc
		addsi r0, r0, 4 	<-inc sp
		stw r0, r5, 0 		<-push acc into stack
		addsi r1, r5, 0 	<-compute t0's addr (to sit in the stack with a offset of 0 from fp)
		addsi r0, r0, 4 	<-inc sp
		stw r0, r5, 0 		<-push t0's addr into stack
		ldw r0, r6, 0 		<-pop t0's addr into op1
		addsi r0, r0, -4 	<-dec sp
		ldw r0, r7, 0 		<-pop pid + 1's result into op2
		addsi r0, r0, -4 	<-dec sp
		stw r6, r7, 0 		<-store pid + 1's value into t0

