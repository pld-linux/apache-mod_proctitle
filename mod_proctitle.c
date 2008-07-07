/* 
 * set process name to currently served vhost
 * 2008, Arkadiusz Miskiewicz <arekm/maven.pl>
 * apache license
 */

#include "ap_config.h"
#include "httpd.h"
#include "http_config.h"
#include "http_request.h"
#include "http_log.h"
#include "http_protocol.h"
#include "util_filter.h"
#include "apr.h"
#include "apr_strings.h"
#include "apr_lib.h"

#define MAXTITLE 1024

static char *title_progname_full;
static char *proctitle_argv=NULL;

module AP_MODULE_DECLARE_DATA proctitle_module;

static void apache_setproctitle(char *arg) {
	if (proctitle_argv) {
		int name_len = strlen(title_progname_full);
		memcpy(proctitle_argv, title_progname_full, name_len);
		if (arg) {
			int arg_len, sep_len;
			char *sep;

			sep = ": ";
			sep_len = strlen(sep);

			arg_len = strlen(arg);
			if (arg_len>MAXTITLE)
				arg_len=MAXTITLE;

			memcpy(proctitle_argv+name_len,sep,sep_len);
			memcpy(proctitle_argv+name_len+sep_len,arg,arg_len);
			proctitle_argv[arg_len+name_len+sep_len]='\0';
		} else {
			proctitle_argv[name_len]='\0';
		}
	}
}

static int apache_proctitle_enter (request_rec *r) {
	/* We only call change_hat for the main request, not subrequests */
	if (r->main) 
		return OK;
	apache_setproctitle(r->server->server_hostname);
	return OK;
}

static int apache_proctitle_exit (request_rec *r) {
	apache_setproctitle(NULL);
	return OK;
}

static int apache_proctitle_init (apr_pool_t *p, apr_pool_t *plog, apr_pool_t *ptemp, server_rec *s) {
	char **symbol=NULL;
	if(!proctitle_argv) {
		symbol=dlsym(NULL,"ap_server_argv0");
		if (symbol)
			proctitle_argv=*symbol;
		title_progname_full = strdup(proctitle_argv);
		if (!title_progname_full)
			proctitle_argv = NULL;
	}
	return OK;
}

static void register_hooks (apr_pool_t *p) {
	ap_hook_post_config (apache_proctitle_init, NULL, NULL, APR_HOOK_MIDDLE);
	ap_hook_access_checker(apache_proctitle_enter, NULL, NULL, APR_HOOK_FIRST);
	ap_hook_log_transaction(apache_proctitle_exit, NULL, NULL, APR_HOOK_LAST);
}

module AP_MODULE_DECLARE_DATA proctitle_module = {
	STANDARD20_MODULE_STUFF,
	NULL,			/* dir config creater */
	NULL,			/* dir merger --- default is to override */
	NULL,			/* server config */
	NULL,			/* merge server config */
	NULL,			/* command table */
	register_hooks		/* register hooks */
};
