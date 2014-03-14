#	mengl
mengl defines a mixset of C and Pascal language and is hopped a re-targetable compiler compiles it 
to multi instruction sets, but now only employ a mips32-like ins introduced in the book 'cpu自制入門'.

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

###	Program Demo
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

###	Target Instruction Set
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

###	Runtime Structure

			before call:
						 	|			|	    low address
							|			|_		
							|  param0   | \ 
							|	 .		|  \
							|	 .		|  |
							|  paramn	|  |
					fp->	|	oldfp	|  |    current frame
							|	ret 	|  |
							|  local0	|  |
							|	 .		|  |
							|	 .		|  /
							|  localm	|_/
							|	 .		|
							|	 .		|
							|	 .		|
					(sp->)	|	 .		|	
							|	param0	|<-push params
							|	 .		|
							|	 .		|
					sp->	|	paramn	|		
							|			|		
							|			|	   high address

							
			after call:

							|	local0	|  |	old frame
							|	 .		|  |
							|	 .		|  /
							|	localm	|_/
							|	 .		|
							|	 .		|
							|	 .		|
							|			|_
							|  param0   | \
							|	 .		|  \
							|	 .		|  |
							|  paramn	|  |
					fp->	|	oldfp	|  |<-push old fp
							|   ret 	|  |<-push ret address
							|  local0	|  |<-skip local variables
							|	 .		|  |	new frame
							|	 .		|  /
					sp->	|  localm	|_/



			exit call:
										 _
							|  param0   | \ 
							|	 .		|  \
							|	 .		|  |
							|  paramn	|  |
					fp->	|	oldfp	|  |    current frame
							|	ret 	|  |
							|  local0	|  |
							|	 .		|  |
							|	 .		|  / 
							|  localm	|_/
							|	 .		|
							|	 .		|
							|	 .		|
					sp->	|	 .		|	
							|	param0	|	
							|	 .		|
							|	 .		|
					(sp->)	|	paramn	|<-pop params


##	What's Next
early times i employed a simple stack machine model for the easy of register allocation, but it turned out that
it seemed too simple to generate usable ins for too many 'push&pop' operations, so i deleted the implemention
and go on to study some other register allocation skills. 


