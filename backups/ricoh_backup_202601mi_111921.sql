--
-- PostgreSQL database dump
--

\restrict 5eKvasaKHucjBC1Y2gygZpothmEaKOa5at7vudgd5LANtSVcEl4Fh3RYbPLEewS

-- Dumped from database version 16.12
-- Dumped by pg_dump version 16.12

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- Name: printer_status; Type: TYPE; Schema: public; Owner: ricoh_admin
--

CREATE TYPE public.printer_status AS ENUM (
    'online',
    'offline',
    'error',
    'maintenance'
);


ALTER TYPE public.printer_status OWNER TO ricoh_admin;

--
-- Name: printerstatus; Type: TYPE; Schema: public; Owner: ricoh_admin
--

CREATE TYPE public.printerstatus AS ENUM (
    'ONLINE',
    'OFFLINE',
    'ERROR',
    'MAINTENANCE'
);


ALTER TYPE public.printerstatus OWNER TO ricoh_admin;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: printers; Type: TABLE; Schema: public; Owner: ricoh_admin
--

CREATE TABLE public.printers (
    id integer NOT NULL,
    hostname character varying(255) NOT NULL,
    ip_address character varying(45) NOT NULL,
    location character varying(255),
    status public.printerstatus,
    detected_model character varying(100),
    serial_number character varying(100),
    has_color boolean,
    has_scanner boolean,
    has_fax boolean,
    toner_cyan integer,
    toner_magenta integer,
    toner_yellow integer,
    toner_black integer,
    last_seen timestamp with time zone,
    notes text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.printers OWNER TO ricoh_admin;

--
-- Name: printers_id_seq; Type: SEQUENCE; Schema: public; Owner: ricoh_admin
--

CREATE SEQUENCE public.printers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.printers_id_seq OWNER TO ricoh_admin;

--
-- Name: printers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ricoh_admin
--

ALTER SEQUENCE public.printers_id_seq OWNED BY public.printers.id;


--
-- Name: user_printer_assignments; Type: TABLE; Schema: public; Owner: ricoh_admin
--

CREATE TABLE public.user_printer_assignments (
    id integer NOT NULL,
    user_id integer NOT NULL,
    printer_id integer NOT NULL,
    provisioned_at timestamp with time zone DEFAULT now(),
    is_active boolean,
    notes text
);


ALTER TABLE public.user_printer_assignments OWNER TO ricoh_admin;

--
-- Name: user_printer_assignments_id_seq; Type: SEQUENCE; Schema: public; Owner: ricoh_admin
--

CREATE SEQUENCE public.user_printer_assignments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_printer_assignments_id_seq OWNER TO ricoh_admin;

--
-- Name: user_printer_assignments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ricoh_admin
--

ALTER SEQUENCE public.user_printer_assignments_id_seq OWNED BY public.user_printer_assignments.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: ricoh_admin
--

CREATE TABLE public.users (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    codigo_de_usuario character varying(8) NOT NULL,
    network_username character varying(255) NOT NULL,
    network_password_encrypted text NOT NULL,
    smb_server character varying(255) NOT NULL,
    smb_port integer NOT NULL,
    smb_path character varying(500) NOT NULL,
    func_copier boolean NOT NULL,
    func_printer boolean NOT NULL,
    func_document_server boolean NOT NULL,
    func_fax boolean NOT NULL,
    func_scanner boolean NOT NULL,
    func_browser boolean NOT NULL,
    email character varying(255),
    department character varying(100),
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.users OWNER TO ricoh_admin;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: ricoh_admin
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO ricoh_admin;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ricoh_admin
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: printers id; Type: DEFAULT; Schema: public; Owner: ricoh_admin
--

ALTER TABLE ONLY public.printers ALTER COLUMN id SET DEFAULT nextval('public.printers_id_seq'::regclass);


--
-- Name: user_printer_assignments id; Type: DEFAULT; Schema: public; Owner: ricoh_admin
--

ALTER TABLE ONLY public.user_printer_assignments ALTER COLUMN id SET DEFAULT nextval('public.user_printer_assignments_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: ricoh_admin
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: printers; Type: TABLE DATA; Schema: public; Owner: ricoh_admin
--

COPY public.printers (id, hostname, ip_address, location, status, detected_model, serial_number, has_color, has_scanner, has_fax, toner_cyan, toner_magenta, toner_yellow, toner_black, last_seen, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: user_printer_assignments; Type: TABLE DATA; Schema: public; Owner: ricoh_admin
--

COPY public.user_printer_assignments (id, user_id, printer_id, provisioned_at, is_active, notes) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: ricoh_admin
--

COPY public.users (id, name, codigo_de_usuario, network_username, network_password_encrypted, smb_server, smb_port, smb_path, func_copier, func_printer, func_document_server, func_fax, func_scanner, func_browser, email, department, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Name: printers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ricoh_admin
--

SELECT pg_catalog.setval('public.printers_id_seq', 1, false);


--
-- Name: user_printer_assignments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ricoh_admin
--

SELECT pg_catalog.setval('public.user_printer_assignments_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ricoh_admin
--

SELECT pg_catalog.setval('public.users_id_seq', 1, false);


--
-- Name: printers printers_pkey; Type: CONSTRAINT; Schema: public; Owner: ricoh_admin
--

ALTER TABLE ONLY public.printers
    ADD CONSTRAINT printers_pkey PRIMARY KEY (id);


--
-- Name: printers printers_serial_number_key; Type: CONSTRAINT; Schema: public; Owner: ricoh_admin
--

ALTER TABLE ONLY public.printers
    ADD CONSTRAINT printers_serial_number_key UNIQUE (serial_number);


--
-- Name: user_printer_assignments user_printer_assignments_pkey; Type: CONSTRAINT; Schema: public; Owner: ricoh_admin
--

ALTER TABLE ONLY public.user_printer_assignments
    ADD CONSTRAINT user_printer_assignments_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: ricoh_admin
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_printers_hostname; Type: INDEX; Schema: public; Owner: ricoh_admin
--

CREATE INDEX ix_printers_hostname ON public.printers USING btree (hostname);


--
-- Name: ix_printers_id; Type: INDEX; Schema: public; Owner: ricoh_admin
--

CREATE INDEX ix_printers_id ON public.printers USING btree (id);


--
-- Name: ix_printers_ip_address; Type: INDEX; Schema: public; Owner: ricoh_admin
--

CREATE UNIQUE INDEX ix_printers_ip_address ON public.printers USING btree (ip_address);


--
-- Name: ix_user_printer_assignments_id; Type: INDEX; Schema: public; Owner: ricoh_admin
--

CREATE INDEX ix_user_printer_assignments_id ON public.user_printer_assignments USING btree (id);


--
-- Name: ix_users_codigo_de_usuario; Type: INDEX; Schema: public; Owner: ricoh_admin
--

CREATE INDEX ix_users_codigo_de_usuario ON public.users USING btree (codigo_de_usuario);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: ricoh_admin
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: ricoh_admin
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: ix_users_name; Type: INDEX; Schema: public; Owner: ricoh_admin
--

CREATE INDEX ix_users_name ON public.users USING btree (name);


--
-- Name: user_printer_assignments user_printer_assignments_printer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ricoh_admin
--

ALTER TABLE ONLY public.user_printer_assignments
    ADD CONSTRAINT user_printer_assignments_printer_id_fkey FOREIGN KEY (printer_id) REFERENCES public.printers(id) ON DELETE CASCADE;


--
-- Name: user_printer_assignments user_printer_assignments_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ricoh_admin
--

ALTER TABLE ONLY public.user_printer_assignments
    ADD CONSTRAINT user_printer_assignments_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict 5eKvasaKHucjBC1Y2gygZpothmEaKOa5at7vudgd5LANtSVcEl4Fh3RYbPLEewS

