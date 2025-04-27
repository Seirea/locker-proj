async function run_sql(cmd) {
	return fetch("http://localhost:5000/admin-execute-sql", {
		"method": "POST",
		"body": cmd,
	});
}

while (true) {
	let req = await run_sql(prompt("sql_exec>"));
	console.log(await req.text());
}
