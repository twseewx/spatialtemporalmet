PGDMP     ;    #                v        
   spatial_db    9.6.8    10.3     �           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                       false            �           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                       false            �           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                       false            �           1262    177815 
   spatial_db    DATABASE     |   CREATE DATABASE spatial_db WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'en_US.UTF-8' LC_CTYPE = 'en_US.UTF-8';
    DROP DATABASE spatial_db;
             twsee    false                        2615    2200    public    SCHEMA        CREATE SCHEMA public;
    DROP SCHEMA public;
             postgres    false            �           0    0    SCHEMA public    COMMENT     6   COMMENT ON SCHEMA public IS 'standard public schema';
                  postgres    false    4                        3079    12655    plpgsql 	   EXTENSION     ?   CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;
    DROP EXTENSION plpgsql;
                  false            �           0    0    EXTENSION plpgsql    COMMENT     @   COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';
                       false    1                        3079    177816    postgis 	   EXTENSION     ;   CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;
    DROP EXTENSION postgis;
                  false    4            �           0    0    EXTENSION postgis    COMMENT     g   COMMENT ON EXTENSION postgis IS 'PostGIS geometry, geography, and raster spatial types and functions';
                       false    2            �            1259    179291    flight_geometries    TABLE     #  CREATE TABLE public.flight_geometries (
    campaign text NOT NULL,
    date date NOT NULL,
    every30points public.geometry,
    every60points public.geometry,
    boundingbox public.geometry,
    rdp2dline public.geometry,
    rdp3dline public.geometry,
    sipsmetgen public.geometry
);
 %   DROP TABLE public.flight_geometries;
       public         twsee    false    2    2    4    2    4    2    4    2    4    2    4    2    4    4    2    4    2    2    4    2    4    2    4    2    4    2    4    2    4    4    2    4    2    2    4    2    4    2    4    2    4    2    4    2    4    4    2    4    2    2    4    2    4    2    4    2    4    2    4    2    4    4    2    4    4    2    2    4    2    4    2    4    2    4    2    4    2    4    4    2    4    2    2    4    2    4    2    4    2    4    2    4    2    4    4    2    4            �          0    179291    flight_geometries 
   TABLE DATA               �   COPY public.flight_geometries (campaign, date, every30points, every60points, boundingbox, rdp2dline, rdp3dline, sipsmetgen) FROM stdin;
    public       twsee    false    201   �       >          0    178113    spatial_ref_sys 
   TABLE DATA               X   COPY public.spatial_ref_sys (srid, auth_name, auth_srid, srtext, proj4text) FROM stdin;
    public       twsee    false    187   �       �      x������ � �      >      x������ � �     